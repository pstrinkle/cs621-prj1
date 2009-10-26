
package proj;

import java.io.IOException;

import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.RawLocalFileSystem;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.util.ToolRunner;
import org.apache.hadoop.util.Tool;

/**
 * ProjectOne
 *
 * Creates an inverted index over all the words in a document corpus, mapping
 * each observed word to a list of filename@offset locations where it occurs.
 *
 * @author(tri1, corbin2)
 */
public class ProjectOne extends Configured implements Tool {
	
	private static final String MAXMINAVG = "maxminavg";
	private static final String MED = "med";
	
	private static final String HDFS = "hdfs";
	private static final String LOCAL = "local";

	/** Driver for the actual MapReduce process */
	private void runJob(String type, String inType, String in, String out) throws IOException {

		JobConf conf = new JobConf(getConf(), ProjectOne.class);

		// repeatedly used paths
		Path outfile = new Path(out + "/" + type + ".txt");
		Path hdfstemp = new Path("temp/part-00000");
		Path tempout = new Path("temp");
		
		if (inType.equals(LOCAL)) {
			FileSystem.get(conf).copyFromLocalFile(new Path(in), new Path(in));
		} else {
			// already in hdfs
		}
		
		FileInputFormat.addInputPath(conf, new Path(in));
		FileOutputFormat.setOutputPath(conf, tempout);
		
		// delete the output file if it exists already
		FileSystem.get(conf).delete(tempout, true);
		FileSystem.get(conf).delete(outfile, true);
		
		//conf.setNumReduceTasks(0);
		conf.setInputFormat(MultiLineTextInputFormat.class);
		conf.setOutputKeyClass(Text.class);

		if (type.equals(MAXMINAVG)) {
			conf.setMapperClass(MaxMinAvgMapper.class);
			conf.setReducerClass(MaxMinAvgReducer.class);
			conf.setOutputValueClass(Text.class);
		} else if (type.equals(MED)) {
			conf.setMapperClass(MedianMapper.class);
			conf.setReducerClass(MedianReducer.class);
			conf.setOutputValueClass(DoubleWritable.class);
		} else {
			System.console().printf("Currently unsupported: %s\n", type);
			return;
		}

		conf.setJobName("Value Processing: " + type);

		JobClient.runJob(conf);

		// all the nodes can access it;
		// so i'm copying all the data to an output location in the HDFS for the project

		// for us i copy the data down to the location filesystem
		RawLocalFileSystem rlfs = new RawLocalFileSystem();
		Path localout = new Path(rlfs.getHomeDirectory().toString() + "/" + type + ".txt");
		
		// copy it to local file system
		FileSystem.get(conf).copyToLocalFile(hdfstemp, localout);
		
		// copy it to the output location in the HDFS
		FileSystem.get(conf).mkdirs(new Path(out));
		FileSystem.get(conf).rename(hdfstemp, outfile);
		FileSystem.get(conf).delete(tempout, true);
	}

  	private boolean verifyArgs(String[] args) {

  		if (args.length != 4) {
  			return false;
  		}

  		if (args[0].equals(MAXMINAVG) || args[0].equals(MED)) {
  			// do nothing
  		} else {
  			// do not bother with second check
  			return false;
  		}
  		
  		if (args[1].equals(HDFS) || args[1].equals(LOCAL)) {
  			// do nothing
  		} else {
  			return false;
  		}
  		
  		return true;
  	}

	public int run(String[] args) throws IOException {

		// args[0] is option
		// args[1] is input-type
		// args[2] is input path
		// args[3] is output path
		
		if (verifyArgs(args)) {
			runJob(args[0], args[1], args[2], args[3]);
		} else {
			System.console().printf("usage: hadoop jar projects.jar ");
			System.console().printf("proj.ProjectOne option input-type input output\n");
			System.console().printf("options: maxminavg, or med\n");
			System.console().printf("input-type: hdfs, local");
			System.exit(-1);
		}

		FileSystem.printStatistics();

		return 0;
	}

	public static void main(String[] args) throws Exception {

		int ret = ToolRunner.run(new ProjectOne(), args);
		System.exit(ret);
	}
}
