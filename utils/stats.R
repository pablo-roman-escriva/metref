library(corrplot)
library(ggplot2)
library(viridis)
library(ggfortify)
library(ggpubr)

args = commandArgs(trailingOnly=TRUE)

sample_size_correlations = 30
sample_size_pca = 70

print(paste0("argumentos",args))

data <- read.csv(paste0("temp/",args[1],".csv"), header=TRUE, stringsAsFactors=FALSE)
data <- data[ , which(names(data) %in% c("tax_selection","gs","bb","hapaxes","entropy","genome_size","gc_content","protein_coding_genes"))]

colnames(data)[colnames(data) == "gs"] ="GS"
colnames(data)[colnames(data) == "bb"] ="BB"
colnames(data)[colnames(data) == "hapaxes"] ="% Hapax"
colnames(data)[colnames(data) == "entropy"] = "Entropy"
colnames(data)[colnames(data) == "genome_size"] ="Genome size"
colnames(data)[colnames(data) == "gc_content"] ="% GC"
colnames(data)[colnames(data) == "protein_coding_genes"] ="Protein c. genes"


pdf(file = paste0("temp/study_analysis_",args[1],".pdf"), paper="a4r", width=12, height=8)
par(mar=c(0,0,0.5,0.5))
par(mfrow = c(1,1))

if (length(unique(data$tax_selection)) > 1) {
  for (taxon in unique(data$tax_selection)) {
   taxon_data <- data[data$tax_selection == taxon,]
   if (nrow(taxon_data) >= sample_size_correlations ) {
    taxon_data <- taxon_data[ , -which(names(taxon_data) %in% c("tax_selection"))]
    title <- paste0("Correlation matrix - ", taxon)
    res1 <- cor.mtest(taxon_data)
    pAdj <- p.adjust(c(res1[[1]]), method = "BH")
    resAdj <- matrix(pAdj, ncol = dim(res1[[1]])[1])
    colnames(resAdj) <- colnames(taxon_data)
    rownames(resAdj) <- colnames(taxon_data)
   
    corrplot(
     cor(taxon_data), title=title, type = 'lower', method = 'ellipse', tl.pos = 'lt',
     sig.level = 0.05, tl.col = 'black', p.mat = resAdj, mar=c(0,0,1,0)
    )
    corrplot(cor(taxon_data), type = 'upper', add = TRUE, tl.pos = 'n', method = 'number',
            col ='black', cl.pos = 'n', number.cex = 0.75)
   }
  }
}
data2 <- data[ , -which(names(data) %in% c("tax_selection"))]
if (nrow(data2) >= sample_size_correlations ) {
  title <- "Correlation matrix - Whole dataset"
  res1 <- cor.mtest(data2)
  pAdj <- p.adjust(c(res1[[1]]), method = "holm")
  resAdj <- matrix(pAdj, ncol = dim(res1[[1]])[1])
  colnames(resAdj) <- colnames(data2)
  rownames(resAdj) <- colnames(data2)


corrplot(
  cor(data2), title=title, type = 'lower', method = 'ellipse', tl.pos = 'lt',
  sig.level = 0.05, tl.col = 'black', p.mat = resAdj, mar=c(0,0,1,0)
)
corrplot(cor(data2), type = 'upper', add = TRUE, tl.pos = 'n', method = 'number',
         col ='black', cl.pos = 'n', number.cex = 0.75)

}
par(mar=c(0,0,0,0))

if (nrow(data) >= sample_size_correlations ) {
title <- "Scatter Plot"
scatter_plot <- ggplot(data, aes(GS, BB, colour = tax_selection))
scatter_plot + geom_point() + labs(x = "BB", y = "GS") + scale_color_viridis(discrete = TRUE) + labs(colour = "Taxon") + ggtitle(title) + theme(plot.title = element_text(hjust = 0.5))

for (item in colnames(data)) {
  if (item != "BB" && item != "GS" && item != "tax_selection") {
    title <- "Scatter Plot"
    scatter_plot <- ggplot(data, aes(x=!!(sym(item)), y=GS, colour = tax_selection))
    scatter_plot <- scatter_plot + geom_point() + labs(x=item, y="GS") + scale_color_viridis(discrete = TRUE) + labs(colour = "Taxon") + ggtitle(title) + theme(plot.title = element_text(hjust = 0.5))
    print(scatter_plot)
    }
}

for (item in colnames(data)) {
  if (item != "BB" && item != "GS" && item != "tax_selection") {
    title <- "Scatter Plot"
    scatter_plot <- ggplot(data, aes(x=!!(sym(item)), y=BB, colour = tax_selection))
    scatter_plot <- scatter_plot + geom_point() + labs(x=item, y="BB") + scale_color_viridis(discrete = TRUE) + labs(colour = "Taxon") + ggtitle(title) + theme(plot.title = element_text(hjust = 0.5))
    print(scatter_plot)
  }
}
}

if (length(unique(data$tax_selection)) > 1) {
  for (taxon in unique(data$tax_selection)) {
    taxon_data <- data[data$tax_selection == taxon,]
    if (nrow(taxon_data) >= sample_size_pca ) {
      taxon_data_2 <- taxon_data[ , -which(names(taxon_data) %in% c("tax_selection"))]
      title <- paste0("PCA - ", taxon)
      pca <- prcomp(taxon_data_2, center = TRUE, scale. = TRUE) 
      pca.plot <- ggplot2::autoplot(pca, x=1, y=2, alpha = 0.7, data = taxon_data, colour = 'tax_selection', loadings = TRUE, loadings.label = TRUE, loadings.colour = "red", loadings.label.colour = "black", loadings.label.repel=TRUE) 
      pca.plot <- pca.plot + scale_color_viridis(discrete = TRUE) + labs(colour = "Taxon") + ggtitle(title) + theme(plot.title = element_text(hjust = 0.5))
      print(pca.plot)
    }
  }
}
if (nrow(data2) >= sample_size_pca ) {
  title <- paste0("PCA - Whole dataset")
  pca <- prcomp(data2, center = TRUE, scale. = TRUE) 
  pca.plot <- ggplot2::autoplot(pca, x=1, y=2, data = data, alpha = 0.7, colour = 'tax_selection', loadings = TRUE, loadings.label = TRUE, loadings.colour = "red", loadings.label.colour = "black", loadings.label.repel=TRUE) 
  pca.plot <- pca.plot + scale_color_viridis(discrete = TRUE) + labs(colour = "Taxon") + ggtitle(title) + theme(plot.title = element_text(hjust = 0.5))
  print(pca.plot)
}

if (length(unique(data$tax_selection)) > 1) {
  for (item in colnames(data)) {
    if (item != "tax_selection") {
      if (nrow(data >= sample_size_correlations )) {
        total_plot <- ggplot(data, aes(x=tax_selection, y=!!(sym(item)), fill=tax_selection, color=tax_selection)) + 
        ylab(item) + xlab("Taxon") + 
        geom_boxplot(alpha=0.7) + 
        theme_bw() + 
        theme(legend.position = "none", axis.text.x = element_text(size=12,angle = 45, vjust = 1, hjust = 1), axis.text.y = element_text(size=12)) + 
        theme(aspect.ratio=0.8) + 
        expand_limits(y = (max(data[[item]])*1.010))+ 
        scale_color_viridis(discrete = TRUE) + scale_fill_viridis(discrete = TRUE) + 
        ggtitle("Boxplot") + theme(plot.title = element_text(hjust = 0.5)) + theme(text=element_text(size=12))
        if (length(unique(data$tax_selection)) == 2) {
          total_plot <- total_plot + stat_compare_means( aes(label = ..p.signif..), label.x = 1.5, label.y = max(data[[item]])*1.01, size = 6)
        }
        else if (length(unique(data$tax_selection)) > 2) {
          total_plot <- total_plot + stat_compare_means(method = "anova",label.y = max(data[[item]])*1.01, size =4)
        }
        print(total_plot)
      }
    }
  }
}
cor.mtest <- function(mat, conf.level = 0.95) {
  mat <- as.matrix(mat)
  n <- ncol(mat)
  p.mat <- lowCI.mat <- uppCI.mat <- matrix(NA, n, n)
  diag(p.mat) <- 0
  diag(lowCI.mat) <- diag(uppCI.mat) <- 1
  for (i in 1:(n - 1)) {
    for (j in (i + 1):n) {
      tmp <- cor.test(x = mat[, i], y = mat[, j], conf.level = conf.level)
      p.mat[i, j] <- p.mat[j, i] <- tmp$p.value
      lowCI.mat[i, j] <- lowCI.mat[j, i] <- tmp$conf.int[1]
      uppCI.mat[i, j] <- uppCI.mat[j, i] <- tmp$conf.int[2]
    }
  }
  return(list(p.mat, lowCI.mat, uppCI.mat))
}
