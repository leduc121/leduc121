import fs from "node:fs/promises";
import sharp from "sharp";

const username = process.env.GITHUB_USERNAME || "leduc121";
const scale = 3;
const rankSize = 80;

async function download(url) {
  const response = await fetch(url, {
    headers: { "User-Agent": `${username}-profile-readme` },
  });

  if (!response.ok) {
    throw new Error(`Request failed (${response.status}): ${url}`);
  }

  return Buffer.from(await response.arrayBuffer());
}

const insightsUrl =
  `https://git-hub-insights-two.vercel.app/api/insight?username=${username}` +
  "&theme=github_dark&graph=true&languages=true&streak=true" +
  "&stats=true&header=true&summary=true&profile=true" +
  "&hide_langs=HTML%2CCSS%2CMakefile";

const rankUrl =
  `https://github-stats-extended.vercel.app/api?username=${username}` +
  "&rank_icon=percentile&hide=stars,commits,prs,issues,contribs" +
  "&hide_title=true&hide_border=true&bg_color=00000000";

const [insightsResponse, rankResponse] = await Promise.all([
  download(insightsUrl),
  download(rankUrl),
]);

const originalInsights = insightsResponse.toString("utf8");
const customBuilderBadge = `
      <g transform="translate(290, 58)">
        <circle cx="36" cy="36" r="40" fill="#0d1117" stroke="#58a6ff" stroke-width="2.5"/>
        <circle cx="36" cy="36" r="32" fill="#58a6ff" opacity="0.12"/>
        <text x="36" y="43" text-anchor="middle" font-size="20" font-weight="700" fill="#7affd9" font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" letter-spacing="1">DEV</text>
      </g>
      <g transform="translate(286, 146)">
        <rect x="0" y="0" width="80" height="20" rx="6" fill="#0d1117" stroke="#58a6ff" stroke-width="1" stroke-opacity="0.7"/>
        <text x="40" y="14" text-anchor="middle" font-size="9" font-weight="600" fill="#7affd9" font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" letter-spacing="0.8">BUILDER</text>
      </g>`;

const customizedInsights = originalInsights.replace(
  /<g transform="translate\(290, 58\)">[\s\S]*?<\/g>\s*<g transform="translate\(296, 146\)">[\s\S]*?<\/g>/,
  customBuilderBadge,
);

if (customizedInsights === originalInsights) {
  throw new Error("Could not replace the third-party letter rank with the custom builder badge");
}

const insightsSvg = Buffer.from(customizedInsights);

const rankMarkup = rankResponse.toString("utf8");
const rankMatch = rankMarkup.match(
  /data-testid="percentile-rank-value"[\s\S]*?>\s*([\d.]+)%\s*<\/text>/,
);

if (!rankMatch) {
  throw new Error("Could not extract the GitHub percentile rank");
}

const percentage = Number.parseFloat(rankMatch[1]);
const size = 125;
const center = size / 2;
const radius = 55;
const circumference = 2 * Math.PI * radius;
const progress = circumference * ((100 - percentage) / 100);

const rankSvg = Buffer.from(`
<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <circle cx="${center}" cy="${center}" r="${radius}" stroke="#d9e6f7" stroke-width="10" fill="none" />
  <circle cx="${center}" cy="${center}" r="${radius}" stroke="#4c8fe8" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="${progress} ${circumference}" transform="rotate(-90 ${center} ${center})" />
  <text x="${center}" y="${center - 9}" text-anchor="middle" dominant-baseline="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="20" font-weight="700" fill="#fafafa">Top</text>
  <text x="${center}" y="${center + 13}" text-anchor="middle" dominant-baseline="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="22" font-weight="700" fill="#fafafa">${percentage}%</text>
</svg>`);

const rankPng = await sharp(rankSvg, { density: 300 })
  .resize(rankSize * scale, rankSize * scale)
  .png({ compressionLevel: 9 })
  .toBuffer();

const insightsPng = await sharp(insightsSvg, { density: 300 })
  .png({ compressionLevel: 9 })
  .toBuffer();

await sharp(insightsPng)
  .composite([{ input: rankPng, left: 30 * scale, top: 30 * scale }])
  .png({ compressionLevel: 9 })
  .toFile("github-cards.png");

const metadata = await sharp("github-cards.png").metadata();
await fs.writeFile(
  "github-card-updated.txt",
  `${new Date().toISOString()} | ${username} | top ${percentage}% | ${metadata.width}x${metadata.height}\n`,
);

console.log(`Generated github-cards.png for ${username} (${metadata.width}x${metadata.height})`);
