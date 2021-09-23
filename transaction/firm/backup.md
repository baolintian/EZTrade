this.callServer(this.obj, "default").then(res => {



})

this.msgbox.success("开始运行");





var Files = Java.type('java.nio.file.Files');

var Paths = Java.type('java.nio.file.Paths');

var StandardCopyOption = Java.type("java.nio.file.StandardCopyOption");



this.logger.info("in Firm App execute backend");

this.logger.info(obj.oid.toString());



//1. 创建相关的工作目录

//2. 更新系统中的元数据



function buildEnv(planPath, taskOid, creatorOid){

  var File = Java.type("java.io.File");

  var FileOutputStream = Java.type("java.io.FileOutputStream");

  var SAXReader = Java.type("org.dom4j.io.SAXReader");

  var XMLWriter = Java.type("org.dom4j.io.XMLWriter");

  var OutputFormat = Java.type("org.dom4j.io.OutputFormat");



  this.logger.info("in buildEnv function");



  let targetFileStream = null;

  let targetWriter = null;



  //模板文件

  let dir = Paths.get("/firm");

  let input = new File(`${dir}${File.separator}param.xml`);



  let inputFile = new File(`${planPath}${File.separator}param.xml`);

  try {



​    let reader = new SAXReader();

​    let document = reader.read(input);



​    // 改写内容

​    document.clearContent();

​    root = document.addElement("parameters");

​    // 写入剖分文件列表

​    

​    // 写入输出文件

​    

​    layer1 = root.addElement("param");



​    layer1

​    .addAttribute("name", "userOid")

​    .setText(creatorOid.toString());



​    layer1 = root.addElement("param");

​    layer1

​    .addAttribute("name", "taskOid")

​    .setText(taskOid.toString());





​    layer1 = root.addElement("param");

​    layer1

​    .addAttribute("name", "paramPath")

​    .setText(planPath.toString());



​    

​    // 重新写入param.xml

​    let format = OutputFormat.createPrettyPrint();

​    targetFileStream = new FileOutputStream(inputFile);

​    targetWriter = new XMLWriter(targetFileStream, format);  

​    targetWriter.write(document);



  } catch(ex) {

​    this.logger.error(ex.toString());

​    this.res = ex.toString();

  } finally{

​    this.logger.info("finally");

​    if (targetWriter) targetWriter.close();

​    if (targetFileStream) targetFileStream.close();

  }

}





planPath = Paths.get("/firm")

nowTime = Date.now().toString();

tempPath = obj.firmName.toString()+"-"+nowTime;

planPath = planPath.resolve(tempPath);

if (Files.notExists(planPath)){

  Files.createDirectory(planPath);   

}



//拷贝配置文件

if(this.omf.getFilePath(obj.firmChosenAlgorithm, "FirmAlgorithm", "firmAlgorithmConfig")){

  this.logger.info("have config file");

  let tmpPath = Paths.get(this.omf.getFilePath(obj.firmChosenAlgorithm, "FirmAlgorithm", "firmAlgorithmConfig"));

  targetPath = planPath.resolve('config.json');

  //源文件 => 拷贝到 targetPath

  Files.copy(tmpPath, targetPath, StandardCopyOption.REPLACE_EXISTING);

}



if(this.omf.getFilePath(obj.firmChosenAlgorithm, "FirmAlgorithm", "firmAlgorithmFile")){

  this.logger.info("have strategy file");

  let tmpPath = Paths.get(this.omf.getFilePath(obj.firmChosenAlgorithm, "FirmAlgorithm", "firmAlgorithmFile"));

  targetPath = planPath.resolve('strategy.py');

  //源文件 => 拷贝到 targetPath

  Files.copy(tmpPath, targetPath, StandardCopyOption.REPLACE_EXISTING);

  

  frameFile = Paths.get("/firm").resolve("main.py");

  targetPath = planPath.resolve('main.py');

  Files.copy(frameFile, targetPath, StandardCopyOption.REPLACE_EXISTING);

}



//buildEnv(路径, taskOid, 虚拟账户Oid, 币种)

buildEnv("/firm/"+tempPath, obj.oid, obj.firmCreator);

obj.firmRunStartTime = (Date.now()).toString();

this.logger.info(obj.firmRunStartTime.toString());

this.omf.edit(obj, "FirmApp");

python_path = "/firm/"+tempPath+"/"+"main.py";

config_path = "/firm/"+tempPath+"/"+"config.json";

xml_path = "/firm/"+tempPath;

output_path = "/firm/"+tempPath+"/output.log"

this.logger.info("nohup python3 "+python_path+" "+config_path+" "+xml_path+" >/dev/null 2>&1 &");

this.sh.execute("nohup python3 "+python_path+" "+config_path+" "+xml_path+" >/dev/null 2>&1 &");

this.sh.execute(`echo 2333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333 >> /test.txt`);

this.logger.info(`nohup python3 ${"/firm/"+tempPath+"/"+"main.py " +"/firm/"+tempPath+"/"+"config.json"+ " /firm/"+tempPath} >> ${"/firm/"+tempPath}/output.log >/dev/null 2>&1 &`);