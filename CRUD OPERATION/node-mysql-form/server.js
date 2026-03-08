const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const db = require('./db');

const app = express();

app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('public'));

app.post('/submit', (req, res) => {
    const { user_id, email, phone } = req.body;
    const sql = "INSERT INTO users (user_id, email, phone) VALUES (?, ?, ?)";
    
    db.query(sql, [user_id, email, phone], (err) => {
        if(err) return res.send(err);
        res.send("Data Saved Successfully!");
    });
});

app.listen(3000, () => {
    console.log("Server running on http://localhost:3000");
});