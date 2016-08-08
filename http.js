const express = require("express"); // Routes
const app = express();
const http = require("http");
const server = http.Server(app);
const router = express.Router(); // Router (express 4.0)



app.use(express.static("client")); // Définition de la racine

router.get("/", (req,res) => { // Renvoi index.html
    res.status(200);
    res.set({"content-type": "text/html; charset=utf-8"});
    res.sendFile("index.html", {root: path.join(__dirname, "client")});
});

app.use("/", router); // Chemin de base

app.on("error", (error) => { // Erreur
    console.log("Error :" + error.message);
    console.log(error.stack);
});

server.on("error", (error) => { // Erreur
    console.log("Error :" + error.message);
    console.log(error.stack);
});

server.listen(8080, () => { // Ecoute sur le port 8080
    console.log("Bomberman running on port 8080");
});
