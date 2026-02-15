const express = require('express');
const config = require('./config');
const setupRoutes = require('./routes');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = config.port || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

setupRoutes(app);

app.use(errorHandler);

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});