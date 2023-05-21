package pw.edu.pl;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

import org.apache.hadoop.mapreduce.lib.input.FileSplit;

public class CosineSimilarity {

  public static class TokenizerMapper extends Mapper<Object, Text, Text, Text> {


    private Text fileName = new Text();
    private Text bagOfWords = new Text();

    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
      // Extract the file name from the input path
      String fileNameWithExtension = ((FileSplit) context.getInputSplit()).getPath().getName();
      String fileNameWithoutExtension = fileNameWithExtension.substring(0, fileNameWithExtension.lastIndexOf('.'));
      
      // Split the text into words
      String[] words = value.toString().split("\\s+");

      // Create a bag of words
      Map<String, Integer> wordCount = new HashMap<>();
      for (String word : words) {
        wordCount.put(word, wordCount.getOrDefault(word, 0) + 1);
      }

      // Convert the bag of words to a string
      StringBuilder bagOfWordsBuilder = new StringBuilder();
      for (Map.Entry<String, Integer> entry : wordCount.entrySet()) {
        bagOfWordsBuilder.append(entry.getKey()).append(":").append(entry.getValue()).append(",");
      }

      // Set the output key-value pair
      fileName.set(fileNameWithoutExtension);
      bagOfWords.set(bagOfWordsBuilder.toString());
      
      // Key - file name
      // Value - bagOfWords
      context.write(fileName, bagOfWords);
    }
  }

  public static class CosReducer extends Reducer<Text, Text, Text, Text> {

    public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
      List<String> bagOfWordsList = new ArrayList<>();

      // Collect all the bag-of-words for the current key
      for (Text value : values) {
        bagOfWordsList.add(value.toString());
      }

      // Set the output key-value pair
      Text outputKey = new Text(key.toString() + " - test ");
      Text outputValue = new Text("0.5");
      
      // Emit the key-value pair
      context.write(outputKey, outputValue);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
    if (otherArgs.length != 2) {
      System.err.println("Usage: wordcount <in> <out>");
      System.exit(2);
    }
    Job job = new Job(conf, "cosine count");
    job.setJarByClass(CosineSimilarity.class);
    job.setMapperClass(TokenizerMapper.class);
    job.setCombinerClass(CosReducer.class);
    job.setReducerClass(CosReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setMapOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(otherArgs[0]));
    FileOutputFormat.setOutputPath(job, new Path(otherArgs[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
