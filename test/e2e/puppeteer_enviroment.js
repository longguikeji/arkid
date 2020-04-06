const PuppeteerEnviromenent = require('jest-environment-puppeteer');
class CustomEnvironmemnt extends PuppeteerEnviromenent {
    async setup() {
        await super.setup();
    }

    async teardown() {
        await super.teardown()
    }

}
module.exports = CustomEnvironmemnt