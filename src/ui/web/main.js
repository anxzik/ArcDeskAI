const { app, BrowserWindow } = require('electron');


let mainWindow;app.on('ready', () => {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    },
  });  mainWindow.loadFile('/home/arch/PycharmProjects/ArcDeskAI/ArcDeskAI/src/ui/web/index.html');
});app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});