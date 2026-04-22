const express = require("express");
const axios = require("axios");
const path = require("path");
const app = express();

const API_URL = globalThis.process?.env?.API_URL || "http://api:8000";

app.use(express.json());
app.use(express.static(path.resolve("views")));

app.post("/submit", async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch {
    res.status(500).json({ error: "something went wrong" });
  }
});

app.get("/status/:id", async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch {
    res.status(500).json({ error: "something went wrong" });
  }
});

app.get("/health", (req, res) => {
  res.json({ status: "OK" });
});

app.listen(3000, () => {
  console.log("Frontend running on port 3000");
});
