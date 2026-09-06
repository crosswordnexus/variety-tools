'use strict';

const esbuild = require('esbuild');
const path = require('path');

async function build() {
  console.log('Building browser bundles...');

  // 1. Minified bundle for production
  await esbuild.build({
    entryPoints: [path.join(__dirname, 'browser.js')],
    bundle: true,
    minify: true,
    sourcemap: true,
    format: 'iife',
    globalName: 'DupeCheckerModule',
    outfile: path.join(__dirname, 'dist', 'dupe-checker.min.js'),
  });

  console.log('Build complete:');
  console.log('  - dist/dupe-checker.min.js');
}

build().catch(err => {
  console.error('Build failed:', err);
  process.exit(1);
});
