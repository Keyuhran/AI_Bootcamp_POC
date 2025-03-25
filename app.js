const express = require('express');
const cors = require('cors');
const path = require('path');
const dotenv = require('dotenv');
const { createClient } = require('@supabase/supabase-js');
const dataController = require('./controllers/dataController');
const multer = require('multer');
const fs = require('fs');
const { spawn } = require('child_process');
const { summarizeEmail } = require('./controllers/summarizeEmailBody');

dotenv.config({ path: path.resolve(__dirname, '.env') });

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Multer setup for file uploads
const upload = multer({ dest: 'uploads/' });

// Serve static files from the `Frontend_test` directory
const frontendPath = path.join(__dirname, 'Frontend_test');
app.use(express.static(frontendPath));

// Store extracted email text in memory
let storedEmailText = "";
let storedEmailSender = "";
let storedEmailSubject = "";
let storedEmailBody = "";
let storedEmailScore = 0;
let storedEmailSummary = "";

// POST /analyze-file — file upload and sentiment processing
app.post('/analyze-file', upload.single('file'), async (req, res) => {
    const filePath = req.file.path;
    const python = spawn('python', ['nlp.py', filePath]);

    let output = '';

    python.stdout.on('data', (data) => {
        const chunk = data.toString();
        console.log("[PYTHON STDOUT]:", chunk);
        output += chunk;
    });

    python.stderr.on('data', (data) => {
        console.error("[PYTHON ERROR]:", data.toString());
    });

    python.on('close', async (code) => {
        fs.unlink(filePath, () => {}); // cleanup uploaded file

        if (code !== 0) {
            return res.status(500).json({ response: 'Error analyzing file' });
        }

        try {
            const json = JSON.parse(output.trim());
            storedEmailText = json.emailText;
            storedEmailSender = json.emailSender;
            storedEmailSubject = json.emailSubject;
            storedEmailBody = json.emailBody;
            storedEmailScore = json.score;
            storedEmailSummary = await summarizeEmail(storedEmailBody);

            res.json({
                summary: `The email you uploaded has a sentiment score of ${storedEmailScore}`,
                showDetails: true,
                emailText: storedEmailText,
                emailSender: storedEmailSender,
                emailSubject: storedEmailSubject,
                emailBody: storedEmailBody,
                emailScore: storedEmailScore,
                emailSummary: storedEmailSummary
              });
        } catch (err) {
            console.error("JSON parse error:", err);
            res.json({ response: output.trim() });
        }
    });
});

// GET /get-email-content — serves stored email text
app.get('/get-email-content', (req, res) => {
    res.json({
        emailText: storedEmailText,
        emailSender: storedEmailSender,
        emailSubject: storedEmailSubject,
        emailBody: storedEmailBody,
        emailScore: storedEmailScore,
        emailSummary: storedEmailSummary
    });
});

// GET /api/interactions — returns monthly interaction data
app.get('/api/interactions', async (req, res) => {
    try {
        const interactions = await dataController.fetchLastFiveMonthsInteractions();
        res.json(interactions);
    } catch (error) {
        console.error("❌ Failed to fetch interactions:", error);
        res.status(500).json({ error: 'Failed to fetch interaction data' });
    }
});

// Route: serve `details.html`
app.get('/details', (req, res) => {
    res.sendFile(path.join(frontendPath, 'details.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
