import {Page, launch} from 'puppeteer';

    export class setAction{
        public async setting(page:Page){

            const setBtn = await page.waitForSelector('a[href="#/workspace/userinfo"]');
            await setBtn.click();

            const personBtn = await page.waitForSelector('.ui-workspace-userinfo--summary .ivu-btn.ivu-btn-default');
            await personBtn.click();

            page.waitFor(3000);

        }
    }
