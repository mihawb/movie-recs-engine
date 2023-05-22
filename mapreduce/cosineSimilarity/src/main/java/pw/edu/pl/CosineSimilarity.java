package pw.edu.pl;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

import info.debatty.java.stringsimilarity.Cosine;

public class CosineSimilarity {

  public static class TokenizerMapper extends Mapper<LongWritable, Text, Text, DocumentWritable> {

    public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
      // Extract the file name from the input path
      String fileNameWithExtension = ((FileSplit) context.getInputSplit()).getPath().getName();
      String fileNameWithoutExtension = fileNameWithExtension.substring(0, fileNameWithExtension.lastIndexOf('.'));

      // Extract document content
      String document = value.toString();

      // Transform to lowercase;
      document = document.toLowerCase();

      // Remove all punctuation marks from document
      document.replaceAll("\\p{Punct}", "");

      // Create document information
      DocumentWritable dw = new DocumentWritable(new Text(fileNameWithoutExtension), new Text(document));
      
      // Key - 1
      // Value - DocumentWritable(document ID, words)
      context.write(new Text("key"), dw);
    }
  }

  public static class CosReducer extends Reducer<Text, DocumentWritable, Text, DoubleWritable> {
    List<DocumentWritable> documents;
    Cosine cosine = new Cosine();

    public void reduce(IntWritable key, Iterable<DocumentWritable> values, Context context) throws IOException, InterruptedException {
      documents = new ArrayList<>();

      for (DocumentWritable dw : values){
        documents.add(new DocumentWritable(dw.getKey(), dw.getValue()));
      }

      for(int i = 0; i < documents.size(); i++){
        for(int j = i + 1; j < documents.size(); j++){
          String k = documents.get(i).toString() + "@" + documents.get(j).toString();

          double similarity = cosine.similarity(documents.get(i).getValue().toString(), documents.get(j).getValue().toString());

          context.write(new Text(k), new DoubleWritable(similarity));
        }
      }
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
    if (otherArgs.length != 2) {
      System.err.println("Usage: wordcount <in> <out>");
      System.exit(2);
    }
    Job job = new Job(conf, "Cosine Similarity");
    job.setJarByClass(CosineSimilarity.class);
    job.setMapperClass(TokenizerMapper.class);
    job.setCombinerClass(CosReducer.class);
    job.setReducerClass(CosReducer.class);

    job.setMapOutputKeyClass(Text.class);
    job.setMapOutputValueClass(DocumentWritable.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(DoubleWritable.class);
    
    FileInputFormat.addInputPath(job, new Path(otherArgs[0]));
    FileOutputFormat.setOutputPath(job, new Path(otherArgs[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
