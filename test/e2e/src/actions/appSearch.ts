import {Page, launch} from 'puppeteer';

 
export class appSearchAction{
    public async appinformation(page:Page,searchName:string){

        const deskBtn = await page.waitForSelector('.ivu-menu-item.ivu-menu-item-active.ivu-menu-item-selected');
        deskBtn.click();
        await page.waitFor(3000);

        const appInput = await page.waitForSelector('.ivu-input.ivu-input-default.ivu-input-with-suffix');
        appInput.type(searchName);
        await page.keyboard.press('Enter');

    }
}

