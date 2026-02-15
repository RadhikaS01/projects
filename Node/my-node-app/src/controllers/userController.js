const User = require('../models/userModel');
exports.createUser = async (req, res) => {
try {
const user = new User(req.body);
await user.save();
res.status(201).send(user);
} catch (error) {
res.status(400).send(error);
}
};

exports.getUsers = async (req, res) => {
try {
const users = await User.find();
res.status(200).send(users);
} catch (error) {
res.status(500).send(error);
}
};