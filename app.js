const express = require('express');
const cors = require('cors');
const path = require('path');
const dotenv = require('dotenv');
const { createClient } = require('@supabase/supabase-js');
const dataController = require('./controllers/dataController');
const multer = require('multer');
const fs = require('fs');
const bcrypt = require('bcrypt');
const { spawn } = require('child_process');
const { summarizeEmail } = require('./controllers/summarizeEmailBody');
const { categorizeEmail } = require('./controllers/categorization');

dotenv.config({ path: path.resolve(__dirname, '.env') });

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Multer setup for file uploads
const upload = multer({ dest: 'uploads/' });

// Serve static files from Frontend_test
const frontendPath = path.join(__dirname, 'Frontend_test');
app.use(express.static(frontendPath));

// Memory storage for email content
let storedEmailText = "";
let storedEmailSender = "";
let storedEmailSubject = "";
let storedEmailBody = "";
let storedEmailScore = 0;
let storedEmailSummary = "";


const hashedPassword = process.env.UPLOAD_PASSWORD_HASH;

app.post('/verify-password', async (req, res) => {
  const { password } = req.body;
  const valid = await bcrypt.compare(password, hashedPassword);
  if (valid) {
    res.sendStatus(200);
  } else {
    res.sendStatus(401);
  }
});

// File analysis route
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
    fs.unlink(filePath, () => {});

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

// Text analysis route
app.post('/analyze-text', async (req, res) => {
  let { text } = req.body;
  if (!text) return res.status(400).json({ error: 'Missing text' });

  if (text.startsWith("Analyse this file:")) {
    text = text.replace("Analyse this file:", "").trim();
  }

  const tempFilePath = `uploads/temp_${Date.now()}.txt`;
  fs.writeFileSync(tempFilePath, text, 'utf8');

  const python = spawn('python', ['nlp.py', tempFilePath]);
  let output = '';

  python.stdout.on('data', (data) => output += data.toString());
  python.stderr.on('data', (data) => console.error("[PYTHON ERROR]:", data.toString()));

  python.on('close', async (code) => {
    fs.unlink(tempFilePath, () => {});
    if (code !== 0) {
      return res.status(500).json({ response: 'Error analyzing text' });
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

// Upload .msg file to archive
// To this:
app.post('/upload-msg', upload.array('files'), async (req, res) => {
  try {
    const files = req.files;

    if (!files || files.length === 0) {
      return res.status(400).json({ message: 'No files uploaded.' });
    }

    const targetDir = path.join(__dirname, 'data/Queries Received and Email Responses');

    for (const file of files) {
      const destPath = path.join(targetDir, file.originalname);
      fs.renameSync(file.path, destPath);
    }

    res.json({ message: `${files.length} file(s) uploaded successfully.` });
  } catch (err) {
    console.error('Upload failed:', err);
    res.status(500).json({ message: 'Upload failed.' });
  }
});

// Enquiry creation
app.post('/create-enquiry', async (req, res) => {
  const { description, sentiment } = req.body;
  if (!description || typeof sentiment !== 'number') {
    return res.status(400).json({ error: "Missing enquiry data" });
  }

  try {
    const cleanedDescription = description.replace(/^Analyse this file:\\s*/i, "").trim();
    const category = await categorizeEmail(cleanedDescription);

    const result = await dataController.createEnquiry(cleanedDescription, category, sentiment);
    res.json({ message: "Enquiry created", result });
  } catch (error) {
    console.error("❌ Failed to create enquiry:", error);
    res.status(500).json({ error: "Failed to create enquiry" });
  }
});

// Interaction creation
app.post('/create-interaction', async (req, res) => {
  try {
    const result = await dataController.createInteraction();
    res.json({ message: 'Interaction created successfully', result });
  } catch (error) {
    console.error("❌ Failed to create interaction:", error);
    res.status(500).json({ error: 'Failed to create interaction' });
  }
});

// Email content
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

// Chart data
app.get('/api/interactions', async (req, res) => {
  try {
    const interactions = await dataController.fetchLastFiveMonthsInteractions();
    res.json(interactions);
  } catch (error) {
    console.error("❌ Failed to fetch interactions:", error);
    res.status(500).json({ error: 'Failed to fetch interaction data' });
  }
});

app.get('/api/categories', async (req, res) => {
  try {
    const categoryCounts = await dataController.fetchAllCategoryCounts();
    res.json(categoryCounts);
  } catch (error) {
    console.error("❌ Failed to fetch category counts:", error);
    res.status(500).json({ error: 'Failed to fetch category data' });
  }
});

// Static page: details.html
app.get('/details', (req, res) => {
  res.sendFile(path.join(frontendPath, 'details.html'));
});

// Start server
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
