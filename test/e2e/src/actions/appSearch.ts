import {Page, launch} from 'puppeteer';

export class appSearchAction{
    public async appinformation(page:Page,searchName:string){

        await page.waitFor(2000);

        const appInput = await page.waitForSelector('.ivu-input.ivu-input-default.ivu-input-with-suffix');
        await  appInput.type(searchName);

        console.log("11111111");
    }
}

