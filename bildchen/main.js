const puppeteer = require('puppeteer');
const fs = require('fs');
const csvParser = require('csv-parser');
const path = require('path');

let data = [];

// Ensure the icons directory exists
const iconsDir = path.join(__dirname, 'icons');
if (!fs.existsSync(iconsDir)){
    fs.mkdirSync(iconsDir);
}

fs.createReadStream('main.csv')
  .pipe(csvParser())
  .on('data', (row) => {
    data.push(row);
  })
  .on('end', async () => {
    console.log('CSV file successfully processed');
    // Generate screenshots for all items in the CSV file
    for (const item of data) {
      const htmlTemplate = generateHTMLTemplate(item.icon, item.text);
      const screenshotPath = await takeScreenshot(htmlTemplate, item.text);
      console.log(`Generated screenshot for ${item.text}`);
    }
  });
  
async function takeScreenshot(htmlTemplate, text) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setContent(htmlTemplate, { waitUntil: 'networkidle0' });
  await page.setViewport({ width: 580, height: 800 });

  const screenshotPath = path.join(__dirname, 'icons', `${text}.png`);
  await page.screenshot({ path: screenshotPath, omitBackground: true });

  await browser.close();

  return screenshotPath;
}

function generateHTMLTemplate(icon, text) {
  // Calculate font size based on text length
  let fontSize = 100; // default font size
  if (text.length > 10) {
    fontSize = 75; // reduce font size for longer text
  }
  if (text.length > 15) {
    fontSize = 50; // further reduce for even longer text
  }

  return `
  <!DOCTYPE html>
  <html lang="en">
  <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Technology Showcase</title>
  <link href="https://fonts.googleapis.com/css2?family=Righteous&display=swap" rel="stylesheet">
  <style>
    :root {
      --random-color: hsl(calc(360 * var(--random)), 70%, 75%);
      --random: 2;
    }

    body {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      background-color: #f0f0f0;
    }

    .outer-box {
      border: 10px solid black;
      width: 500px;
      height: 750px;
      margin: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      border-radius: 100px;
      overflow: hidden;
      background: linear-gradient(to bottom, transparent 520px, black 520px, black 524px, transparent 524px), var(--random-color);
    }

    .image-container {
      width: 100%;
      height: 480px;
      padding: 10px;
      box-sizing: border-box;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .image-container img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }

    .text-container {
      height: 350px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: ${fontSize}px;
      font-family: 'Righteous';
    }
  </style>
  <script>
    document.documentElement.style.setProperty('--random', Math.random());
  </script>
  </head>
  <body style="background: transparent;">

  <div class="outer-box">
    <div class="image-container">
      <img src="${icon}" alt="${text} Logo">
    </div>
    <div class="text-container">${text}</div>
  </div>

  </body>
  </html>
  `;
}