load_all_graphics_funcs <- function(){
  # Load graphics functions in a source code directory
  # The list contains all file name without extension
  # For example: plot.R --> plot
  result <- list()
  file_paths <- Sys.glob("data/raw-data/schema/R-4.3.2-graphics/*.R")
  for (file_path in file_paths){
    filename_we <- tools::file_path_sans_ext( basename(file_path) )
    result <- append(result, filename_we)
  }
  return(result)
}

load_all_graphics_funcs_2 <- function(){
  result <- load_all_graphics_funcs()
  lines <- readLines(file("graphics_funcs.txt"))
  for(line in lines){
    result <- append(result, line)
  }
  return(result)
}

recur_extract_call_expr <- function(node){
  # Recursively extract all call nodes
  # Return: list of call node
  if (is.call(node) == FALSE){
    return(list())
  } else {
    return_list <- list(node)
    for (i in 1:length(node)){
      child_calls = recur_extract_call_expr(node[[i]])
      return_list <- c(return_list, child_calls)
    }
    return(return_list)
  }
}


extract_plot_func_call <- function(node){
  # Extract call node for a function. 
  # The format is: function_name(args, kargs)
  # Return: list(func_name=func_name, args=args, kargs=kargs)
  func_name <- node[[1]]
  args = list()
  kargs <- list()
  keywords <- names(node)
  if (is.null(keywords)){
    if (length(node) > 1){
      for (i in 2: length(node)){
        args <- append(args, deparse(node[[i]]))
      }
    }
    return_list <- list(func_name=func_name, args=args, kargs=list())
    return(return_list)
  } else{
    for (i in 2:length(keywords)){
      keyword <- toString(keywords[i])
      value <-   deparse(node[[i]])
      if (keyword != ""){
        kargs[keyword] <- value
      } else {
        args <- append(args, value)
      }
    }
    return_list <- list(func_name=func_name, args=args, kargs=kargs)
    return(return_list)
  }
}

handle_call_node <- function(node, function_list){
  # Handle node in general
  
  # if assign, only for update function_list
  if ((node[[1]] == "<-" || node[[1]] == "=") && length(node)==3){
    # TODO: handling
    return(list(result=NULL, function_list=function_list))
  } else {
    # if function
    # check if the function_name is in function_list
    if ( toString(node[[1]]) %in% function_list){
      result <- extract_plot_func_call(node)
      return(list(result=result, function_list=function_list))
    } else {
      return(list(result=NULL, function_list=function_list))
    }
  }
}

handle_call_node_2 <- function(node, function_list){
  # if assign, only for update function_list
  if ((node[[1]] == "<-" || node[[1]] == "=") && length(node)==3){
    # TODO: handling
    if( is.symbol(node[[3]]) && toString(node[[3]]) %in% function_list){
      return(deparse(node))
    }
  }
}

main <- function(){
  graphics_func_list_1 = load_all_graphics_funcs()
  graphics_func_list_2 = load_all_graphics_funcs_2()
  print(length(graphics_func_list_1))
  print(length(graphics_func_list_2))
  
  expr_list <- parse(file = "sample1.R")
  for (expr in expr_list){
    print(expr)
    print("-----")
    nodes <- recur_extract_call_expr(expr)
    for(node in nodes){
      handle_call_node_2(node, graphics_func_list)
    }
    print("--------------------")
  }
  
}
