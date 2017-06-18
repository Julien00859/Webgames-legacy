const chai = require('chai');
const should = chai.should();
const chaiHttp = require('chai-http');
const {hashPassword, verifyPassword, generateJWT} = require('../model/user-model');
const {register, login, resetPassword, logout} = require('../model/user-model');

chai.use(chaiHttp);

describe('hashing', _ => {
  it('should encrypt password (bcrypt)', done => {
    const password = 'superabricot2000formula1';
    hashPassword(password).then(hash => {
      response.should.exist;
      hash.sould.be.a('string');
    });
  });

  it('should validate the password if match', done => {
    const password = 'superabricot2000formula1';
    hashPassword(password).then(hash => {
      verifyPassword(password, hash).then(response => {
        response.should.be.true;
      });
    });
  })
});
