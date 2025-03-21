const express = require('express');
const cors = require('cors');
const path = require('path');
const dotenv = require('dotenv');
const { createClient } = require('@supabase/supabase-js');
const dataController = require('./controllers/dataController');
const multer = require('multer');
const fs = require('fs');
const { spawn } = require('child_process');

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

// POST /analyze-file — file upload and sentiment processing
app.post('/analyze-file', upload.single('file'), (req, res) => {
    const filePath = req.file.path;
    const python = spawn('python', ['nlp.py', filePath]);

    let output = '';

    python.stdout.on('data', (data) => {
        const chunk = data.toString();
        console.log("[PYTHON STDOUT]:", chunk); // 👈 add this line
        output += chunk;
    });

    python.stderr.on('data', (data) => {
        console.error("[PYTHON ERROR]:", data.toString());
    });
    
    python.on('close', (code) => {
        fs.unlink(filePath, () => {}); // cleanup uploaded file

        if (code !== 0) {
            return res.status(500).json({ response: 'Error analyzing file' });
        }

        try {
            const json = JSON.parse(output.trim());
            storedEmailText = json.emailText; // Store the extracted email text
            console.log("[DEBUG] Stored Email Text:", storedEmailText);
            res.json(json);
        } catch (err) {
            console.error("JSON parse error:", err);
            res.json({ response: output.trim() });
        }
    });
});

// GET /get-email-content — serves stored email text
app.get('/get-email-content', (req, res) => {
    res.json({ emailText: storedEmailText });
});

// Route: serve `details.html`
app.get('/details', (req, res) => {
    res.sendFile(path.join(frontendPath, 'details.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
