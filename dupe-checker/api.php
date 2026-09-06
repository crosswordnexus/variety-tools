<?php
/**
 * Dupe Checker API Endpoint
 *
 * Secure PHP wrapper that invokes the Node.js dupe-checker engine on demand
 * with strict security guardrails (no shell execution, hard timeouts, size caps).
 *
 * Usage:
 *   POST /api.php (JSON body: {"words": ["quick", "quickly"], "stopwords": ["up"]})
 *   GET  /api.php?words=quick,quickly&stopwords=up
 */

// -----------------------------------------------------------------------------
// Guardrail 1: HTTP & CORS Headers
// -----------------------------------------------------------------------------
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json; charset=utf-8');

// Handle preflight OPTIONS request immediately
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit(0);
}

// -----------------------------------------------------------------------------
// Guardrail 2: Payload Size Cap (Max 64 KB)
// -----------------------------------------------------------------------------
$contentLength = isset($_SERVER['CONTENT_LENGTH']) ? (int)$_SERVER['CONTENT_LENGTH'] : 0;
if ($contentLength > 65536) {
    http_response_code(413);
    echo json_encode(['error' => 'Payload too large. Maximum body size is 64 KB.']);
    exit(0);
}

$rawInput = file_get_contents('php://input');
if (strlen($rawInput) > 65536) {
    http_response_code(413);
    echo json_encode(['error' => 'Payload too large. Maximum body size is 64 KB.']);
    exit(0);
}

// -----------------------------------------------------------------------------
// Guardrail 3: Strict Input Parsing & Sanitization
// -----------------------------------------------------------------------------
$words = [];
$stopwords = [];
$minWordLength = 2;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode($rawInput, true);
    if ($rawInput !== '' && $data === null) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid JSON body format.']);
        exit(0);
    }
    if (is_array($data)) {
        $words = isset($data['words']) && is_array($data['words']) ? $data['words'] : [];
        $stopwords = isset($data['stopwords']) && is_array($data['stopwords']) ? $data['stopwords'] : [];
        if (isset($data['minWordLength'])) {
            $minWordLength = max(1, min(20, (int)$data['minWordLength']));
        }
    }
} else {
    // GET request support via query parameters
    if (isset($_GET['words'])) {
        $words = preg_split('/[\n,]+/', (string)$_GET['words']);
    }
    if (isset($_GET['stopwords'])) {
        $stopwords = preg_split('/[\n,]+/', (string)$_GET['stopwords']);
    }
    if (isset($_GET['minWordLength'])) {
        $minWordLength = max(1, min(20, (int)$_GET['minWordLength']));
    }
}

// Sanitize and enforce item counts & string length limits
// Cap at 500 words, max 60 chars per word; strip null bytes & control chars
$cleanWords = [];
foreach ($words as $w) {
    if (count($cleanWords) >= 500) break;
    $str = preg_replace('/[\x00-\x1F\x7F]/', '', trim((string)$w));
    $str = mb_substr($str, 0, 60, 'UTF-8');
    if ($str !== '') {
        $cleanWords[] = $str;
    }
}

$cleanStopwords = [];
foreach ($stopwords as $s) {
    if (count($cleanStopwords) >= 100) break;
    $str = preg_replace('/[\x00-\x1F\x7F]/', '', trim((string)$s));
    $str = mb_substr($str, 0, 30, 'UTF-8');
    if ($str !== '') {
        $cleanStopwords[] = strtolower($str);
    }
}

if (empty($cleanWords)) {
    echo json_encode([
        'hasDupes' => false,
        'dupes' => [],
        'stemCounts' => new stdClass(),
        'entries' => [],
        'error' => 'No words provided'
    ]);
    exit(0);
}

// -----------------------------------------------------------------------------
// Guardrail 4: Zero-Shell Direct Subprocess Execution
// -----------------------------------------------------------------------------
// 1. Check optional local config.php
$config = [];
if (file_exists(__DIR__ . '/config.php')) {
    $config = include __DIR__ . '/config.php';
    if (!is_array($config)) $config = [];
}

// 2. Resolve Node binary path:
//    a) config.php 'node_bin'
//    b) getenv('NODE_BIN')
//    c) Standard system paths (/usr/local/bin/node, /usr/bin/node)
//    d) Default fallback 'node'
$nodeBin = isset($config['node_bin']) && $config['node_bin'] !== '' ? $config['node_bin'] : getenv('NODE_BIN');

if (!$nodeBin) {
    if (file_exists('/usr/local/bin/node')) {
        $nodeBin = '/usr/local/bin/node';
    } elseif (file_exists('/usr/bin/node')) {
        $nodeBin = '/usr/bin/node';
    } else {
        $nodeBin = 'node';
    }
}

$cliPath = __DIR__ . '/cli.js';
if (!file_exists($cliPath)) {
    http_response_code(500);
    echo json_encode(['error' => 'cli.js not found on server.']);
    exit(0);
}

// Passing command as an array bypasses /bin/sh shell invocation completely
$cmd = [
    $nodeBin,
    '--max-old-space-size=128', // Memory cap
    $cliPath,
    '--stdin',
    '--json'
];

$descriptors = [
    0 => ['pipe', 'r'], // stdin (pipe to send JSON)
    1 => ['pipe', 'w'], // stdout (pipe to read result)
    2 => ['pipe', 'w']  // stderr (pipe to read errors)
];

$process = @proc_open($cmd, $descriptors, $pipes, __DIR__);

if (!is_resource($process)) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to initialize Node process on server.']);
    exit(0);
}

// Pass JSON data strictly via stdin stream
$inputPayload = json_encode([
    'words' => $cleanWords,
    'stopwords' => $cleanStopwords,
    'minWordLength' => $minWordLength
]);

fwrite($pipes[0], $inputPayload);
fclose($pipes[0]);

// -----------------------------------------------------------------------------
// Guardrail 5: Hard 3-Second Execution Timeout
// -----------------------------------------------------------------------------
stream_set_blocking($pipes[1], false);
stream_set_blocking($pipes[2], false);

$stdout = '';
$stderr = '';
$startTime = microtime(true);
$timeoutSec = 3.0;
$timedOut = false;

while (true) {
    $readPipes = [$pipes[1], $pipes[2]];
    $writePipes = null;
    $exceptPipes = null;

    $ready = @stream_select($readPipes, $writePipes, $exceptPipes, 0, 100000); // 100ms slice

    if ($ready > 0) {
        foreach ($readPipes as $p) {
            if ($p === $pipes[1]) {
                $chunk = fread($pipes[1], 8192);
                if ($chunk !== false) $stdout .= $chunk;
            } elseif ($p === $pipes[2]) {
                $chunk = fread($pipes[2], 8192);
                if ($chunk !== false) $stderr .= $chunk;
            }
        }
    }

    $status = proc_get_status($process);
    if (!$status['running']) {
        // Read remaining buffered data
        while (($chunk = fread($pipes[1], 8192))) $stdout .= $chunk;
        while (($chunk = fread($pipes[2], 8192))) $stderr .= $chunk;
        break;
    }

    if ((microtime(true) - $startTime) > $timeoutSec) {
        $timedOut = true;
        // Kill runaway process immediately
        @proc_terminate($process, 9);
        break;
    }
}

fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);

if ($timedOut) {
    http_response_code(504);
    echo json_encode(['error' => 'Dupe check processing timed out (exceeded 3 seconds).']);
    exit(0);
}

// -----------------------------------------------------------------------------
// Final Response Validation
// -----------------------------------------------------------------------------
$trimmedStdout = trim($stdout);
if ($trimmedStdout === '' || json_decode($trimmedStdout) === null) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Subprocess error',
        'details' => trim($stderr) ?: 'Empty output from worker'
    ]);
    exit(0);
}

// Return validated JSON
echo $trimmedStdout;
