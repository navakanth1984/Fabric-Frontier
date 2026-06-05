const puppeteer = require("puppeteer");
const { PuppeteerScreenRecorder } = require("puppeteer-screen-recorder");
const fs = require("fs");
const path = require("path");
const http = require("http");
const { exec } = require("child_process");

async function renderTrailer() {
    console.log("🎬 Initializing HyperFrames Audio-Visual Assembly Pipeline (V2)...");

    // 1. Start HTTP Server
    const server = http.createServer((req, res) => {
        let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
        const extname = String(path.extname(filePath)).toLowerCase();
        const mimeTypes = {
            '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
            '.png': 'image/png', '.jpg': 'image/jpg', '.wav': 'audio/wav', '.mp3': 'audio/mpeg'
        };
        const contentType = mimeTypes[extname] || 'application/octet-stream';

        fs.readFile(filePath, (err, data) => {
            if (err) {
                res.writeHead(404);
                res.end("Not Found");
                return;
            }
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(data);
        });
    }).listen(8086);

    // 2. Launch Puppeteer
    const browser = await puppeteer.launch({
        headless: "new",
        defaultViewport: { width: 1920, height: 1080 },
        args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio']
    });

    const page = await browser.newPage();
    const targetUrl = 'http://localhost:8086/';
    console.log(`🌐 Loading timeline from: ${targetUrl}`);
    
    // Track audio events
    const audioEvents = [];

    page.on('console', msg => {
        const text = msg.text();
        if (text.startsWith("AUDIO_START:") || text.startsWith("BGM_START:")) {
            const parts = text.split(":");
            const type = parts[0];
            const ms = parseInt(parts[1]);
            const file = parts.slice(2).join(":"); // Rejoin path in case of :
            
            // Only add if file exists
            if (fs.existsSync(path.join(__dirname, file))) {
                audioEvents.push({ ms, file });
                console.log(`🎵 Logged Audio Sync: ${file} at ${ms}ms`);
            } else {
                console.log(`⚠️ Skipped Audio (Not found): ${file}`);
            }
        }
    });

    await page.goto(targetUrl);
    await new Promise(r => setTimeout(r, 2000)); // Load assets

    // 3. Start Video Recorder
    const videoFile = path.resolve(__dirname, 'temp_video.mp4');
    const recorder = new PuppeteerScreenRecorder(page, {
        fps: 30,
        quality: 100,
        videoFrame: { width: 1920, height: 1080 }
    });

    console.log("🎥 Starting Video Capture...");
    await recorder.start(videoFile);

    console.log("▶️ Triggering playback...");
    await page.click("#play-btn");

    console.log("⏳ Recording in progress... (this will take ~150 seconds)");
    
    // Wait for the timeline to finish
    await page.waitForFunction(() => {
        const btn = document.getElementById('play-btn');
        return btn && !btn.disabled && btn.innerText === "REPLAY CINEMATIC";
    }, { timeout: 300000 });

    await new Promise(r => setTimeout(r, 2000)); // Fade out buffer
    console.log("🛑 Playback complete. Stopping recording...");
    
    await recorder.stop();
    await browser.close();
    server.close();

    console.log("🎞️ Multiplexing Audio tracks via FFmpeg...");

    if (audioEvents.length === 0) {
        console.log("No audio events found. Exiting early.");
        return;
    }

    // 4. Construct FFmpeg command
    const finalMp4 = path.resolve(__dirname, 'dead_loop_trailer_v3.mp4');
    let ffmpegCmd = `ffmpeg -y -i "${videoFile}" `;
    let filterComplex = "";
    let amixInputs = "";

    // Add inputs
    audioEvents.forEach((audio, idx) => {
        ffmpegCmd += `-i "${path.join(__dirname, audio.file)}" `;
        // Delay filter for this input (Inputs start at 1, Video is 0)
        let volFilter = audio.file.includes("bgm.mp3") ? ",volume=0.2" : "";
        filterComplex += `[${idx + 1}:a]adelay=${audio.ms}|${audio.ms}${volFilter}[a${idx}]; `;
        amixInputs += `[a${idx}]`;
    });

    // Add mix filter
    filterComplex += `${amixInputs}amix=inputs=${audioEvents.length}:duration=longest:dropout_transition=3[a]`;
    
    ffmpegCmd += `-filter_complex "${filterComplex}" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "${finalMp4}"`;

    // console.log("Executing FFmpeg:", ffmpegCmd);

    exec(ffmpegCmd, (error, stdout, stderr) => {
        if (error) {
            console.error(`❌ Error during FFmpeg conversion:\n${stderr}`);
            return;
        }
        
        // Clean up
        fs.unlinkSync(videoFile);
        
        console.log("✅ Render complete! Cinematic trailer assembled at:");
        console.log(`➡️  ${finalMp4}`);
    });
}

renderTrailer().catch(err => {
    console.error("Fatal error during rendering:", err);
});
