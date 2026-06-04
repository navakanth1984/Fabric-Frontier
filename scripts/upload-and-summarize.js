#!/usr/bin/env node
/**
 * upload-and-summarize.js
 * Automates creating a notebook, uploading sources, querying the chat,
 * retrieving the final summary output, and saving it to the Obsidian vault.
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

const NOTEBOOK_NAME = "AI 3D Websites and Assets";
const URLS_FILE = path.join(__dirname, "..", "scratch", "temp_urls.json");
const VAULT_DIR = "c:\\Users\\navka\\navakanth001\\obsidian-vault\\Obsidian Vault\\01-Projects\\AI-Automation";
const HEADLESS = args.headless === 'true' || process.env.HEADLESS === 'true';

const CHROME_USER_DATA = 'C:\\Users\\navka\\AppData\\Local\\Google\\Chrome\\User Data';
const CHROME_EXE = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const CHROME_EXE_86 = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';

async function loadUrls() {
  if (!fs.existsSync(URLS_FILE)) {
    console.error(`ERROR: ${URLS_FILE} not found. Run the prepare step first.`);
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(URLS_FILE, 'utf8'));
  return data.videos.map(v => v.url);
}

async function launchBrowser() {
  const tempProfile = path.join(process.env.TEMP || 'C:\\Temp', 'notebooklm-chrome-profile-summary');
  const defaultDst  = path.join(tempProfile, 'Default', 'Network');
  fs.mkdirSync(defaultDst, { recursive: true });

  // Copy Google login cookies
  const cookieSrc = path.join(CHROME_USER_DATA, 'Default', 'Network', 'Cookies');
  try {
    fs.copyFileSync(cookieSrc, path.join(defaultDst, 'Cookies'));
    console.log('Copied Google login cookies from Chrome.');
  } catch (e) {
    console.warn('Chrome cookies locked — please ensure Chrome is closed if login is required.\n');
  }

  const executablePath =
    fs.existsSync(CHROME_EXE)    ? CHROME_EXE    :
    fs.existsSync(CHROME_EXE_86) ? CHROME_EXE_86 :
    undefined;

  console.log(`Browser: ${executablePath ? 'Google Chrome' : 'Playwright Chromium'} (Headless: ${HEADLESS})\n`);

  const browser = await chromium.launchPersistentContext(tempProfile, {
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

  return browser;
}

async function goToNotebookLM(context) {
  const page = await context.newPage();
  await page.goto('https://notebooklm.google.com', { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(3000);

  const url = page.url();
  if (url.includes('accounts.google.com')) {
    console.log('\nGoogle Sign-in Required.');
    console.log('Please log in manually in the browser window that opened.');
    console.log('Waiting up to 2 minutes for login confirmation...\n');
    await page.waitForURL('**/notebooklm.google.com**', { timeout: 120000 });
    console.log('Logged in successfully.\n');
  } else {
    console.log('Already logged in to NotebookLM.');
  }

  return page;
}

async function createNotebook(page, name) {
  console.log(`\nCreating notebook: "${name}"`);
  const newBtn = page.locator('button:has-text("New notebook"), [aria-label="New notebook"], button:has-text("Create")').first();
  await newBtn.waitFor({ timeout: 20000 });
  await newBtn.click();
  await page.waitForTimeout(3000);

  // Fill title if input dialog is shown
  const titleInput = page.locator('input[placeholder*="title" i], input[placeholder*="name" i]').first();
  if (await titleInput.isVisible({ timeout: 4000 })) {
    await titleInput.clear();
    await titleInput.fill(name);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(2000);
  }
  console.log('Notebook created.');
}

async function addUrlSource(page, url) {
  console.log(`Uploading source: ${url}`);
  const addBtn = page.locator('button:has-text("Add source"), [aria-label*="Add source"], button:has-text("+ Add")').first();
  await addBtn.waitFor({ timeout: 15000 });
  await addBtn.click();
  await page.waitForTimeout(1500);

  const youtubeOpt = page.locator('button:has-text("YouTube"), li:has-text("YouTube")').first();
  const websiteOpt = page.locator('button:has-text("Website"), li:has-text("Website"), button:has-text("URL")').first();

  if (url.includes('youtube.com') || url.includes('youtu.be')) {
    if (await youtubeOpt.isVisible({ timeout: 3000 })) {
      await youtubeOpt.click();
    } else if (await websiteOpt.isVisible({ timeout: 2000 })) {
      await websiteOpt.click();
    }
  } else {
    if (await websiteOpt.isVisible({ timeout: 3000 })) {
      await websiteOpt.click();
    } else if (await youtubeOpt.isVisible({ timeout: 2000 })) {
      await youtubeOpt.click();
    }
  }
  await page.waitForTimeout(1000);

  const urlInput = page.locator('input[type="url"], input[placeholder*="url" i], input[placeholder*="link" i], input[placeholder*="YouTube" i]').first();
  await urlInput.waitFor({ timeout: 5000 });
  await urlInput.fill(url);
  await page.waitForTimeout(500);

  const insertBtn = page.locator('button:has-text("Insert"), button:has-text("Add"), button:has-text("Confirm")').first();
  if (await insertBtn.isVisible({ timeout: 3000 })) {
    await insertBtn.click();
  } else {
    await page.keyboard.press('Enter');
  }
  
  // Wait longer for upload request to complete
  await page.waitForTimeout(5000);
}

async function askNotebookLM(page, query) {
  console.log(`\nQuerying NotebookLM: "${query}"`);
  
  // Locate chat text area
  const chatInput = page.locator('textarea[placeholder*="Ask" i], textarea[placeholder*="chat" i], [contenteditable="true"]').first();
  await chatInput.waitFor({ timeout: 20000 });
  await chatInput.click();
  await chatInput.fill(query);
  await page.waitForTimeout(500);
  
  // Send message
  await page.keyboard.press('Enter');
  console.log('Query submitted. Waiting for response to stream & stabilize...');

  // Track stability of last response bubble
  let lastText = '';
  let stableCycles = 0;
  
  for (let i = 0; i < 45; i++) { // Wait up to 90 seconds
    await page.waitForTimeout(2000);
    const bubbles = page.locator('.chat-bubble, [class*="message" i], [class*="response" i], [class*="answer" i], div[class*="bubble" i]');
    const count = await bubbles.count();
    
    if (count > 0) {
      const currentText = await bubbles.last().innerText().catch(() => '');
      if (currentText.trim() === lastText.trim() && currentText.trim().length > 0) {
        stableCycles++;
        if (stableCycles >= 4) { // stable for 8 seconds
          console.log('Response stabilized.');
          return currentText.trim();
        }
      } else {
        lastText = currentText;
        stableCycles = 0;
      }
    }
  }
  
  return lastText.trim();
}

async function saveToObsidian(summary) {
  const date = new Date().toISOString().split("T")[0];
  const filename = `${date}-ai-3d-websites-and-assets-summary.md`;
  const filepath = path.join(VAULT_DIR, filename);

  const content = `---
date: ${date}
tags: ["notebooklm", "ai-automation", "3d-websites", "meshy-ai", "lovable", "spline-ai", "dora-ai"]
project: "AI-Automation"
source: "NotebookLM Summary"
---

# AI 3D Websites and Assets Summary

${summary}
`;

  fs.mkdirSync(VAULT_DIR, { recursive: true });
  fs.writeFileSync(filepath, content, "utf8");
  console.log(`\n✅ Summary successfully saved to Obsidian: ${filepath}\n`);
  return filepath;
}

async function main() {
  const urls = await loadUrls();
  console.log(`URLs loaded: ${urls.length}`);

  const browser = await launchBrowser();
  const page = await goToNotebookLM(browser);

  try {
    await createNotebook(page, NOTEBOOK_NAME);
    
    // Add all 3 sources
    for (const url of urls) {
      try {
        await addUrlSource(page, url);
      } catch (err) {
        console.error(`Failed to add source: ${url} - ${err.message}`);
      }
    }

    // Wait a brief moment for sources to finish background processing in NotebookLM
    console.log('\nWaiting 15 seconds for sources to process...');
    await page.waitForTimeout(15000);

    // Ask for the consolidated final summary
    const query = "Provide a comprehensive, high-fidelity synthesis of these uploaded materials. Detail the capabilities, use cases, and distinct features of Meshy AI, Dora AI, Lovable, and Spline AI 3D Generation. Summarize how they fit together in a modern workflow to create 3D web experiences.";
    const summary = await askNotebookLM(page, query);

    if (summary) {
      console.log('\n--- RETRIEVED SUMMARY ---');
      console.log(summary);
      console.log('-------------------------\n');
      await saveToObsidian(summary);
    } else {
      console.error('\n❌ ERROR: Failed to retrieve summary response from NotebookLM.');
    }

  } catch (err) {
    console.error('\nExecution error:', err.message);
  } finally {
    console.log('Closing browser context.');
    await browser.close();
  }
}

main().catch(err => {
  console.error('\nFatal error:', err.message);
  process.exit(1);
});
