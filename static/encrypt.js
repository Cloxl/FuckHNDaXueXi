const { sm2Encrypt } = require('./static/sm2.js');
function encrypt(ctoken, pubkeySM2, cipherMode) {
    return sm2Encrypt(ctoken, pubkeySM2, cipherMode);
}

module.exports = encrypt;