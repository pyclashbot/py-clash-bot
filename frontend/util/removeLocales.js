//https://www.electron.build/configuration/configuration#afterpack
exports.default = async function (context) {
  //console.log(context)
  const fs = require("fs");
  const localeDir = context.appOutDir + "/locales/";

  fs.readdir(localeDir, function (err, files) {
    //files is array of filenames (basename form)
    if (!(files && files.length)) return;
    for (let i = 0, len = files.length; i < len; i++) {
      const match = files[i].match(/en-US\.pak/);
      if (match === null) {
        fs.unlinkSync(localeDir + files[i]);
      }
    }
  });
};
