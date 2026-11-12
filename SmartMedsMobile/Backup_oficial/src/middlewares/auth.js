const jwt = require('jsonwebtoken');

 

function authenticateToken(req, res, next) {

  const authHeader = req.headers['authorization'];

  // Formato do Header: "Bearer TOKEN"

  const token = authHeader && authHeader.split(' ')[1];

 

  if (!token) {

    return res.status(401).json({ message: 'Acesso negado. Token não fornecido.' });

  }

 

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {

    if (err) {

      return res.status(403).json({ message: 'Token inválido ou expirado.' });

    }

    req.user = user; // Anexa as informações do usuário à requisição

    next();

  });

}

 

module.exports = authenticateToken;