import {Page, launch} from 'puppeteer';

export class organizationAction{
    public async origanization(page:Page){
            
        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();
        await page.waitFor(3000);

    } 
}
