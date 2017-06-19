const chai = require('chai');
const should = chai.should();
const chaiHttp = require('chai-http');
const app = require('../index');
const postgres = require('../postgres');
const {hashPassword, verifyPassword, generateJWT} = require('../model/user-model');

chai.use(chaiHttp);

describe('hashing', _ => {
  it('should encrypt password (bcrypt)', done => {
    const password = 'superabricot2000formula1';
    hashPassword(password).then(hash => {
      hash.should.exist;
      done();
    }).catch(error => {
      error.should.not.exist;
      done();
    })
  });

  it('should validate the password if match', done => {
    const password = 'superabricot2000formula1';
    hashPassword(password).then(hash => {
      verifyPassword(password, hash).then(response => {
        response.should.be.true;
        done();
      }).catch(error => error.should.not.exist);
    }).catch(error => {
      error.should.not.exist;
      done();
    })
  });

  it('should not validate a wrong password', done => {
    const password = 'superabricot2000formula1';
    const wrongPassword = 'abricotpoire';
    hashPassword(password).then(hash => {
      verifyPassword(wrongPassword, hash).then(response => {
        response.should.be.false;
        done();
      }).catch(error => error.should.not.exist);
    }).catch(error => {
      error.should.exist;
      done();
    })
  });
});

describe('authentication', _ => {
  before(done => {
    postgres.sync({force: true});
    done();
  });

  it('should register a new user and save him in the db', done => {
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
      }).catch(error => {
        done();
      })
  });

  it('should not register a user already registered', done => {
    chai.request(app)
      .post('/api/register')
      .send({
        username: 'Matiuso',
        password: 'superabricot2000formula1',
        mail: 'unknown@unknown.com'
      }).then(response => {
        done();
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
      }).then(response => {
        //response.should.be.empty;
        done();
      }).catch(error => {
        error.should.have.status(500);
        //error.response.body.error[0].should.be.eq("Le nom d'utilisateur est vide.");
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
      }).catch(error => {
        done();
      });
  });

  it('should not login an unregistered user', done => {
    chai.request(app)
      .post('/api/login')
      .send({
        username: 'Jacky',
        password: 'superabricot'
      }).then(response => {
        done()
        done();
      }).catch(error => {
        error.should.have.status(404);
        done();
      });
  });
});
