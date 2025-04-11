// The script below contains the hashing algorithm
const bcrypt = require('bcrypt');
bcrypt.hash("test", 10).then(console.log);
