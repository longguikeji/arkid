module.exports = {

  "globalSetup": "jest-environment-puppeteer/setup",
  "globalTeardown": "jest-environment-puppeteer/teardown",
  "testEnvironment": "./puppeteer_enviroment.js",
  
  roots:[
    "<rootDir>"
  ],
  "moduleFileExtensions": [
    "ts",
    "js",
  ],

  "testMatch": [
    "**/*.test.*"
  ],
  "transform": {
    "^.+\\.ts$": "ts-jest"
  }

  


};

