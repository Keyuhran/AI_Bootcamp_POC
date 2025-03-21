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

// API: Fetch interaction data
app.get('/api/interactions', async (req, res) => {
    try {
        const interactions = await dataController.fetchLastFiveMonthsInteractions();
        res.json(interactions);
    } catch (error) {
        console.error('Error fetching interactions:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// POST /analyze-file — file upload and sentiment processing
app.post('/analyze-file', upload.single('file'), (req, res) => {
    const filePath = req.file.path;
    const python = spawn('python', ['nlp.py', filePath]);

    let output = '';

    python.stdout.on('data', (data) => {
        output += data.toString();
    });

    python.stderr.on('data', (data) => {
        console.error(`Python error: ${data}`);
    });

    python.on('close', (code) => {
        fs.unlink(filePath, () => {}); // cleanup uploaded file

        if (code !== 0) {
            return res.status(500).json({ response: 'Error analyzing file' });
        }

        try {
            const json = JSON.parse(output.trim());
            res.json(json);
        } catch (err) {
            console.error("JSON parse error:", err);
            res.json({ response: output.trim() });
        }
    });
});

// Route: serve `data.html`
app.get('/data', (req, res) => {
    res.sendFile(path.join(frontendPath, 'data.html'));
});

// Optional: route for detailed email sentiment analysis
app.get('/details', (req, res) => {
    res.sendFile(path.join(frontendPath, 'details.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
