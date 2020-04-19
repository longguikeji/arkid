import {Page, launch} from 'puppeteer';

export class appSearchAction{
    public async appinformation(page:Page,searchName:string){
       // const returnBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-right > a:nth-child(1) > button');
       // await returnBtn.click();

       // const deskBtn = await page.waitForSelector('a[href="#/workspace/apps"]');
       // deskBtn.click();
        await page.waitFor(2000);

        const appInput = await page.waitForSelector('.ivu-input.ivu-input-default.ivu-input-with-suffix');
        await  appInput.type(searchName);

        console.log("11111111");
    }
}

