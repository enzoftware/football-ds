use polars::prelude::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let df = CsvReadOptions::default()
        .with_infer_schema_length(None)
        .try_into_reader_with_file_path(Some("data/radars10.csv".into()))?
        .finish()?;

    println!("Shape: {:?}", df.shape());
    println!("{}", df.head(Some(3)));
    Ok(())
}
