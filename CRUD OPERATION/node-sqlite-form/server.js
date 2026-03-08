const express = require("express");
const bodyParser = require("body-parser");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();
const PORT = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));

const db = new sqlite3.Database("database.db");

// Table banana
db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT
)`);

// 1. CREATE: Data save karna
app.post("/save", (req, res) => {
    const { name, phone } = req.body;
    db.run("INSERT INTO users (name, phone) VALUES (?, ?)", [name, phone], (err) => {
        if (err) return res.send("Error!");
        res.redirect("/"); // Wapas home page par bhej dega
    });
});

// 2. READ: Data dikhana
app.get("/data", (req, res) => {
    db.all("SELECT * FROM users", [], (err, rows) => {
        if (err) return res.send("Error!");
        res.json(rows); // Browser mein data dikhayega
    });
});

// 3. UPDATE: Data update karna
app.post("/update", (req, res) => {
    const { id, name, phone } = req.body;
    db.run("UPDATE users SET name = ?, phone = ? WHERE id = ?", [name, phone, id], (err) => {
        if (err) return res.send("Error!");
        res.redirect("/");
    });
});

// 4. DELETE: Data khatam karna
app.post("/delete", (req, res) => {
    const { id } = req.body;
    db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
        if (err) return res.send("Error!");
        res.redirect("/");
    });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});