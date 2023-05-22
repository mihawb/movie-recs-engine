package pw.edu.pl;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.Writable;

public final class DocumentWritable implements Writable {
    private Text key;
    private Text value;
    
    public DocumentWritable(){
        key = new Text();
        value = new Text();
    }
    public DocumentWritable(Text key, Text value){
        this.key = new Text(key.toString());
        this.value = new Text(value.toString());
    }
    
    @Override
    public void readFields(DataInput in) throws IOException{
        key.readFields(in);
        value.readFields(in);
    }
    @Override
    public void write(DataOutput out)throws IOException{
        key.write(out);
        value.write(out);
    }
    
    public Text getKey(){
        return this.key;
    }
    public Text getValue(){
        return this.value;
    }
 
    @Override
    public String toString(){
        return this.key.toString()+"\n"+this.value.toString();
    }
}