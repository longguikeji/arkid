import {Page, launch} from 'puppeteer';

    export class setAction{
        public async setting(page:Page, name:string){
            const setBtn = await page.waitForSelector('a[href="#/workspace/userinfo"]');
            await setBtn.click();

            const personBtn = await page.waitForSelector('.ui-workspace-userinfo--summary .ivu-btn.ivu-btn-default');
            await personBtn.click();

            page.waitFor(3000);
            const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
            await nameInput.type(name);

            const addMobileBtn = await page.waitForSelector('.mobile .ivu-btn.ivu-btn-default');
            await addMobileBtn.click();

            const cancelBtn = await page.waitForSelector('.ivu-modal-confirm-footer>button:first-child');
            await cancelBtn.click();

            const addEmailBtn = await page.waitForSelector('.email .ivu-btn.ivu-btn-default');
            await addEmailBtn.click();
            await cancelBtn.click();

            const saveBtn = await page.waitForSelector('.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
            await saveBtn.click();


        }
    }