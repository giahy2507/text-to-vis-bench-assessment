library(jsonlite)
library(readr)
source("utils.R")


parse_content <- function(content){
  tryCatch({
    expr_list <- parse(text = content)
    return(expr_list)
  }, error = function(e){
    return(NULL)
    }
  )
}

main <- function(){
  graphics_func_list <- load_all_graphics_funcs_2()
  print(paste("Number of graphics function: ", length(graphics_func_list)))
  
  # input_path (file) obtained from ../download_thestack.py
  # output_dir is the directory to store the output. You must create the directory first
  input_path = "data/raw-data/R_Graphics.jsonl"
  output_dir = "data/raw-data/R_Graphics"
  
  lines <- read_lines(input_path)
  counter <- 1
  for (line in lines){
    print(paste("Counter ", as.character(counter)))
    counter <- counter + 1
    json_data <- fromJSON(line)
    expr_list = parse_content(json_data$content)
    if(is.null(expr_list)){
      print("Cannot parse!")
      next
    }
    
    hexsha <- json_data$hexsha
    output_path = paste(output_dir, "/", hexsha, ".r.txt", sep="")
    fo <- file(output_path, open="w")

    for (expr in expr_list){
      nodes <- recur_extract_call_expr(expr)
      for (node in nodes){
        tryCatch({
          
          node_result <- handle_call_node(node = node, function_list = graphics_func_list)
          if ( !is.null(node_result$result)){
            # write(node, fo)
            write(node_result$result$func_name, fo)
            write(toJSON(node_result$result$args), fo)
            write(toJSON(node_result$result$kargs), fo)
            write("--------------------", fo)
          }
        }, error = function(e){
          print(node)
        })
      }
    }
    close(fo)
  }
}

main()