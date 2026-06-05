#!/usr/bin/env node
/**
 * infinite-sync.js
 * Part of the Infinite Knowledge Engine (IKE).
 * Automatically reads new/modified Obsidian notes from the vault
 * and uploads them to your NotebookLM vault using Google Chrome session cookies.
 *
 * Usage:
 *   node scripts/infinite-sync.js --notebook "Infinite Knowledge Vault" --days 1
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, val, i, arr) => {
    if (val.startsWith('--')) acc.push([val.slice(2), arr[i + 1]]);
    return acc;
  }, [])
);

const NOTEBOOK_NAME = args.notebook || "Infinite Knowledge Vault";
const DAYS_LIMIT = parseFloat(args.days || "1"); // Only sync notes modified in the last N days
const HEADLESS = args.headless === 'true' || process.env.HEADLESS === 'true';

// Local Workspace Obsidian Path
const OBSIDIAN_DIR = "c:\\Users\\navka\\navakanth001\\obsidian-vault\\Obsidian Vault\\01-Projects\\AI-Automation";
const CHROME_USER_DATA = "C:\\Users\\navka\\AppData\\Local\\Google\\Chrome\\User Data";
const CHROME_EXE = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const CHROME_EXE_86 = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe";

function getRecentNotes(dir, daysLimit) {
  if (!fs.existsSync(dir)) {
    console.error(`Obsidian directory not found: ${dir}`);
    return [];
  }

  const files = fs.readdirSync(dir);
  const now = Date.now();
  const limitMs = daysLimit * 24 * 60 * 60 * 1000;
  const recentFiles = [];

  for (const file of files) {
    if (!file.endsWith('.md')) continue;
    const filePath = path.join(dir, file);
    const stats = fs.statSync(filePath);
    const ageMs = now - stats.mtimeMs;

    if (ageMs <= limitMs) {
      recentFiles.push({
        name: file,
        path: filePath,
        title: file.replace(/\.md$/, ''),
        content: fs.readFileSync(filePath, 'utf8'),
        mtime: stats.mtime
      });
    }
  }

  return recentFiles;
}

async function launchBrowser() {
  const tempProfile = path.join(process.env.TEMP || 'C:\\Temp', 'notebooklm-sync-profile');
  const defaultDst  = path.join(tempProfile, 'Default', 'Network');
  fs.mkdirSync(defaultDst, { recursive: true });

  // Copy Chrome cookies
  const cookieSrc = path.join(CHROME_USER_DATA, 'Default', 'Network', 'Cookies');
  try {
    fs.copyFileSync(cookieSrc, path.join(defaultDst, 'Cookies'));
    console.log('Copied Google login cookies from Chrome profile.');
  } catch (e) {
    console.warn('Chrome cookies locked or not accessible. Proceeding with temporary session.\n');
  }

  const executablePath =
    fs.existsSync(CHROME_EXE)    ? CHROME_EXE    :
    fs.existsSync(CHROME_EXE_86) ? CHROME_EXE_86 :
    undefined;

  return await chromium.launchPersistentContext(tempProfile, {
    headless: HEADLESS,
    executablePath,
    args: [
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-extensions',
      '--disable-blink-features=AutomationControlled',
    ],
    ignoreDefaultArgs: ['--enable-automation'],
    viewport: { width: 1280, height: 900 }
  });
}

async function addCopiedTextSource(page, title, text) {
  // Click Add source
  const addBtn = page.locator('button:has-text("Add source"), [aria-label*="Add source"], button:has-text("+ Add")').first();
  await addBtn.waitFor({ timeout: 10000 });
  await addBtn.click();
  await page.waitForTimeout(1000);

  // Click "Copied text" or "Pasted text" or "Text"
  const copiedTextOpt = page.locator('button:has-text("Copied text"), li:has-text("Copied text"), button:has-text("Paste text")').first();
  await copiedTextOpt.waitFor({ timeout: 5000 });
  await copiedTextOpt.click();
  await page.waitForTimeout(800);

  // Fill in the title and text content
  const titleInput = page.locator('input[placeholder*="Title" i], input[placeholder*="name" i]').first();
  await titleInput.waitFor({ timeout: 5000 });
  await titleInput.fill(title);
  await page.waitForTimeout(300);

  const textInput = page.locator('textarea, [contenteditable="true"]').first();
  await textInput.waitFor({ timeout: 5000 });
  await textInput.fill(text);
  await page.waitForTimeout(500);

  // Click Insert/Add button
  const insertBtn = page.locator('button:has-text("Insert"), button:has-text("Add"), button:has-text("Confirm")').first();
  if (await insertBtn.isVisible({ timeout: 2000 })) {
    await insertBtn.click();
  } else {
    await page.keyboard.press('Enter');
  }
  await page.waitForTimeout(2000);
}

async function main() {
  console.log(`Scanning Obsidian vault at: ${OBSIDIAN_DIR}`);
  const notes = getRecentNotes(OBSIDIAN_DIR, DAYS_LIMIT);
  
  if (notes.length === 0) {
    console.log(`No Obsidian notes modified in the last ${DAYS_LIMIT} days found. Nothing to sync.`);
    return;
  }

  console.log(`Found ${notes.length} note(s) to sync to NotebookLM.`);
  for (const n of notes) {
    console.log(`  - ${n.name} (Modified: ${n.mtime})`);
  }

  console.log('\nLaunching automated browser connection...');
  const context = await launchBrowser();
  const page = await context.newPage();
  
  try {
    await page.goto('https://notebooklm.google.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);

    if (page.url().includes('accounts.google.com')) {
      if (HEADLESS) {
        console.error('\n❌ ERROR: Google login is required, but the browser is running in headless mode.');
        console.error('Please run the sync script WITHOUT "--headless true" first to log in manually:');
        console.error('  node scripts/infinite-sync.js --notebook "Infinite Knowledge Vault" --days 1\n');
        throw new Error('Google authentication required in headed mode.');
      }
      console.log('Google login required. Please verify/log in within the browser window...');
      await page.waitForURL('**/notebooklm.google.com**', { timeout: 120000 });
      console.log('Login verified.');
    }

    // Select or create notebook
    console.log(`Locating notebook: "${NOTEBOOK_NAME}"`);
    const notebookCard = page.locator(`[data-testid*="notebook"]:has-text("${NOTEBOOK_NAME}"), article:has-text("${NOTEBOOK_NAME}"), [class*="NotebookCard"]:has-text("${NOTEBOOK_NAME}")`).first();
    
    if (await notebookCard.isVisible({ timeout: 5000 })) {
      console.log(`Opening existing notebook: "${NOTEBOOK_NAME}"`);
      await notebookCard.click();
    } else {
      console.log(`Creating new notebook: "${NOTEBOOK_NAME}"`);
      const newBtn = page.locator('button:has-text("New notebook"), [aria-label="New notebook"]').first();
      await newBtn.waitFor({ timeout: 5000 });
      await newBtn.click();
      await page.waitForTimeout(2000);

      const titleInput = page.locator('input[placeholder*="title" i]').first();
      if (await titleInput.isVisible({ timeout: 3000 })) {
        await titleInput.clear();
        await titleInput.fill(NOTEBOOK_NAME);
        await page.keyboard.press('Enter');
        await page.waitForTimeout(1500);
      }
    }

    let synced = 0;
    for (const note of notes) {
      console.log(`Syncing note: "${note.title}"...`);
      try {
        await addCopiedTextSource(page, note.title, note.content);
        synced++;
        console.log(`Success: "${note.title}" synced.`);
      } catch (err) {
        console.error(`Failed to sync "${note.title}": ${err.message}`);
      }
    }

    console.log(`\nFeedback sync loop finished. Synced ${synced}/${notes.length} notes.`);
  } finally {
    console.log('Closing browser in 5 seconds...');
    await page.waitForTimeout(5000);
    await context.close();
  }
}

main().catch(err => {
  console.error('Fatal Sync Error:', err.message);
  process.exit(1);
});
