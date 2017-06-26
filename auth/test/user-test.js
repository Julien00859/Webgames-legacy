const chai = require('chai');
const should = chai.should();
const chaiHttp = require('chai-http');
const app = require('../index');
const postgres = require('../postgres');
const {hashPassword, verifyPassword, generateJWT} = require('../model/user-model');

chai.use(chaiHttp);

function decodeToken(token) {
  return new Promise(resolve => {
    const decodedToken = JSON.parse(window.atob(token.split('.')[1]));
    resolve(decodedToken);
  });
}

describe('hashing', _ => {
  it('should encrypt password (bcrypt)', done => {
    const password = 'superabricot2000formula1';
    hashPassword(password).then(hash => {
      hash.should.exist;
      done();
    });
  });

  it('should validate the password if match', done => {
    const password = 'superabricot2000formula1';
    hashPassword(password).then(hash => {
      verifyPassword(password, hash).then(response => {
        response.should.be.true;
        done();
      });
    });
  });

  it('should not validate a wrong password', done => {
    const password = 'superabricot2000formula1';
    const wrongPassword = 'abricotpoire';
    hashPassword(password).then(hash => {
      verifyPassword(wrongPassword, hash).then(response => {
        response.should.be.false;
        done();
      });
    });
  });
});

describe('authentication', _ => {
  before(done => {
    postgres.sync({force: true});
    done();
  });

  it('should register a new user and save it into the db', done => {
    chai.request(app)
      .post('/api/register')
      .send({
        username: 'Matiuso',
        password: 'superabricot2000formula1',
        mail: 'unknown@unknown.com'
      }).then(response => {
        response.should.have.status(200);
        response.should.be.json;
        response.should.redirectTo('/');
        response.body.success.should.be.eq('Utilisateur créé avec succès !');
        done();
      });
  });

  it('should not register a already registered user', done => {
    chai.request(app)
      .post('/api/register')
      .send({
        username: 'Matiuso',
        password: 'superabricot2000formula1',
        mail: 'unknown@unknown.com'
      }).catch(error => {
        error.should.have.status(400);
        error.response.body.error.should.be.eq("le nom d'utilisateur Matiuso est déjà utilisé.");
        done();
      })
  });

  it('should not register a user with empty username', done => {
    chai.request(app)
      .post('/api/register')
      .send({
        username: '',
        password: 'superabricot2000formula1',
        mail: 'unknown@unknown.com'
      }).catch(error => {
        error.should.have.status(500);
        done();
      })
  });

  it('should login a registered user and give back a token (jwt)', done => {
    chai.request(app)
      .post('/api/login')
      .send({
        username: 'Matiuso',
        password: 'superabricot2000formula1'
      }).then(response => {
        response.should.have.status(200);
        response.should.be.json;
        response.body.token.should.be.a('string');
        response.body.should.have.any.keys('token');
        done();
      });
  });

  it('should not login a unregistered user', done => {
    chai.request(app)
      .post('/api/login')
      .send({
        username: 'Jacky',
        password: 'superabricot'
      }).catch(error => {
        error.should.have.status(404);
        done();
      });
  });
});

describe('any profile', _ => {
  it('should show the profile of a given user', done => {
    chai.request(app)
      .get('/api/account/:id')
      .then(response => {
        response.should.have.status(200);
        response.body.should.have.any.keys('username', 'mail');
        done();
      });
  });
});

describe('token routes', _ => {
  let token;

  before(done => {
    chai.request(app)
      .post('/api/login')
      .send({
        username: 'Matiuso',
        password: 'superabricot2000formula1'
      }).then(response => {
        token = response.body.token;
        done();
      });
  });

  it('should show the profile of the connected user', done => {
    chai.request(app)
      .get('/api/account')
      .set('authorization', 'Bearer ' + token)
      .then(response => {
        response.should.have.status(200);
        response.body.should.have.any.keys('username', 'mail');
        done();
      });
  });

  it('should update profile of a logged user', done => {
    chai.request(app)
      .put('/api/account/update')
      .set('authorization', 'Bearer ' + token)
      .send({
        username: 'Matiusoooooo',
      }).then(response => {
        response.should.have.status(200);
        response.body.should.have.any.keys('token');
        decodeToken(response.body.token).then(token => {
          token.u_username.should.be.eq('Matiusoooooo');
          done();
        });
      });
  });

  it('should logout a authenticated user', done => {
    chai.request(app)
      .delete('/api/logout')
      .set('authorization', 'Bearer ' + token)
      .then(response => {
        response.should.have.status(200);
        response.body.should.be.eq('disconnected');
        response.should.redirectTo('/');
        done();
      });
  });
});

describe('forgot password', _ => {
  it('should send an email if password forgot', done => {
    chai.request(app)
      .post('/api/forgot')
      .send({
        mail: 'unknown@unknown.com'
      }).then(response => {
        response.should.have.status(200);
        response.body.should.have.any.keys('success');
        response.body.success.should.be.eq('Email envoyé avec succès à unknown@unknown.com. Vous avez 1 heure.')
        done();
      });
  });

  it('should allow password reset if token and id are valid', done => {
    chai.request(app)
      .put('/api/account/reset')
      .send({
        mail: 'unknown@unknown.com',
        password: 'trololoonsemarreaubistrot'
      }).then(response => {
        response.should.have.status(200);
        response.body.should.have.any.keys('success');
        response.body.success.should.be.eq('mot de passe changé avec succès !');
        done();
      });
  });

  it('should unregister registered user', done => {
    chai.request(app)
      .delete('/api/account/unregister')
      .then(response => {
        response.should.have.status(200);
        response.body.should.have.any.keys('success');
        response.body.success.should.be.eq('désinscription faite !');
        done();
      });
  });
});
