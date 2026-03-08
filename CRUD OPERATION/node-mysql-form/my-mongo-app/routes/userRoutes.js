const express = require("express");
const router = express.Router();
const userCtrl = require("../controllers/userController");

router.get("/", userCtrl.getAllUsers);
router.post("/add", userCtrl.createUser);
router.put("/update/:id", userCtrl.updateUser);
router.delete("/delete/:id", userCtrl.deleteUser);

module.exports = router;