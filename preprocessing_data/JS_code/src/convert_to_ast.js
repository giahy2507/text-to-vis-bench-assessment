const acornLoose = require("acorn-loose");
const fs = require('fs');

function main() {
  // For ChartJS
  // const testFolder = '/Users/nngu0448/Documents/data/the-stack/JavaScript/JavaScript_chartjs';

  // For Vegalite
  const testFolder = '/Users/nngu0448/Documents/usyd/projects/code-gen-4-vis-phase-1/data/raw-data/the-stack/JavaScript_ChartJS';
  const outputFolder = testFolder;
  
  fs.readdir(testFolder, (err, files) => {
    files.forEach( (file) => {
      var file_path = `${testFolder}/${file}`;
      if (file_path.endsWith(".js")){
        console.log(file_path);
        var file_path_json = `${outputFolder}/${file}.ast.json`;
        fs.readFile(file_path, (err, inputD) => {
          if (err) throw err;
          var inputD_str = inputD.toString();
          try {
            var node = acornLoose.parse(inputD_str);
            var json_str = JSON.stringify(node, null, 2);
            fs.writeFile(file_path_json, json_str, (err) => { 
              if (err) 
                console.log(err); 
              else {
                console.log("Writing sucessfully!");
              } 
            }); 
          } catch {
            console.log("Exception!");
          }
        }); 
      }
    });
  });

  
}

if (require.main === module) {
  main();
}
