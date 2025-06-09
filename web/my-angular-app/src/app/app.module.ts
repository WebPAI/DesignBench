// app.module.ts
import { ErrorHandler } from '@angular/core';

class MyErrorHandler implements ErrorHandler {
  handleError(error: any) {
    const errorEl = document.createElement('div');
    errorEl.style.color = 'red';
    errorEl.innerHTML = `<h2>Error: ${error.message}</h2>`;
    document.body.prepend(errorEl);
  }
}

@NgModule({
  providers: [{ provide: ErrorHandler, useClass: MyErrorHandler }]
})
