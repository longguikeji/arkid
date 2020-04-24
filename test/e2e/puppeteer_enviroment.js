
const exec = require('child_process').exec

const syncDataCmd = 'docker cp testdata.sql arkid-db:/'
const loadDataCmd = 'docker exec arkid-db bash -c "mysql -u root -proot arkid < /testdata.sql"'

const PuppeteerEnviromenent = require('jest-environment-puppeteer');
class CustomEnvironmemnt extends PuppeteerEnviromenent {
    async () {
        await super.setup();
        exec(
            syncDataCmd, (error, stdout, stderr) => {
                if (error != null){
                    throw(error)
                }
            },
        )
        exec(
            loadDataCmd, (error, stdout, stderr) =>{
                if (error != null) {
                    throw(error)
                } 
            }
        )
    }

    async teardown() {
        await super.teardown()
    }

}
module.exports = CustomEnvironmemnt