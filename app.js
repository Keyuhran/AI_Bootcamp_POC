const express = require('express');
const cors = require('cors');
const path = require('path');
const dotenv = require('dotenv');
const { createClient } = require('@supabase/supabase-js');
const dataController = require('./controllers/dataController');

dotenv.config({ path: path.resolve(__dirname, '.env') });

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// Serve static files from the `Frontend_test` directory
const frontendPath = path.join(__dirname, 'Frontend_test');
app.use(express.static(frontendPath));

// API route to fetch interactions data
app.get('/api/interactions', async (req, res) => {
    try {
        const interactions = await dataController.fetchLastFiveMonthsInteractions();
        res.json(interactions);
    } catch (error) {
        console.error('Error fetching interactions:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Route to serve `data.html` when accessing `/data`
app.get('/data', (req, res) => {
    res.sendFile(path.join(frontendPath, 'data.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
