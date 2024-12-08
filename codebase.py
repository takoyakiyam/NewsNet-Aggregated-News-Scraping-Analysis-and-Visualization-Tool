import sys
import requests
import json
import networkx as nx
import spacy
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, QCheckBox, QLabel, QDialog,
    QLineEdit, QTabWidget, QGroupBox, QComboBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt')
nltk.download('stopwords')
nlp = spacy.load("en_core_web_md")

# Load topic labels from a JSON file
with open("topic_labels.json", "r") as file:
    TOPIC_LABELS = json.load(file)

def categorize_topic_dynamic(keywords):
        """Categorize a topic using semantic similarity with spaCy."""
        best_label = "Miscellaneous"  # Default label if no match is found
        highest_similarity = 0
        
        for label, keyword_list in TOPIC_LABELS.items():
            label_doc = nlp(" ".join(keyword_list))  # Combine label keywords into a single text
            for keyword in keywords:
                keyword_doc = nlp(keyword)
                similarity = label_doc.similarity(keyword_doc)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_label = label
        return best_label
    
# Scraping functions
def scrape_foxnews():
    url = "https://www.foxnews.com/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return [h3.get_text(strip=True) for h3 in soup.find_all('h3')]

def scrape_philstar():
    url = "https://www.philstar.com/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return [h2.get_text(strip=True) for h2 in soup.find_all('h2')]

def scrape_manilaTimes():
    url = "https://www.manilatimes.net"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    headline_classes = ['article-title-h1', 'article-title-h4', 'article-title-h5']
    headlines = []
    for class_name in headline_classes:
        headlines.extend([div.get_text(strip=True) for div in soup.find_all('div', class_=class_name)])
    return headlines

def scrape_rappler():
    url = "https://www.rappler.com"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return [h3.get_text(strip=True) for h3 in soup.find_all('h3')]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("News Scraper with Improved Layout")
        self.resize(700, 700)

        # Main central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Greeting and date
        self.greeting_label = QLabel("<h2>Greetings, User!</h2>")
        current_date = datetime.now().strftime("%B %d, %Y")
        self.date_label = QLabel(f"Today's Date is <b> {current_date}</b>")
        self.main_layout.addWidget(self.greeting_label)
        self.main_layout.addWidget(self.date_label)

        # Top label
        self.label = QLabel("<h3>Select Websites to Scrape</h3>")
        self.main_layout.addWidget(self.label)

        # Website selection area
        self.website_groupbox = QGroupBox("Websites")
        self.website_layout = QVBoxLayout()
        self.checkbox_foxnews = QCheckBox("Fox News")
        self.checkbox_philstar = QCheckBox("Philstar")
        self.checkbox_manilaTimes = QCheckBox("Manila Times")
        self.checkbox_rappler = QCheckBox("Rappler")
        self.website_layout.addWidget(self.checkbox_foxnews)
        self.website_layout.addWidget(self.checkbox_philstar)
        self.website_layout.addWidget(self.checkbox_manilaTimes)
        self.website_layout.addWidget(self.checkbox_rappler)
        self.website_groupbox.setLayout(self.website_layout)
        self.main_layout.addWidget(self.website_groupbox)

        # Scraping Operations Group
        self.scraping_operations_group = QGroupBox("Scraping Operations")
        self.scraping_operations_layout = QHBoxLayout()
        self.check_all_button = QPushButton("Select All Websites")
        self.check_all_button.clicked.connect(self.toggle_select_all)
        self.scrape_button = QPushButton("Scrape Selected Websites")
        self.scrape_button.clicked.connect(self.scrape_websites)
        self.scraping_operations_layout.addWidget(self.check_all_button)
        self.scraping_operations_layout.addWidget(self.scrape_button)
        self.scraping_operations_group.setLayout(self.scraping_operations_layout)
        self.main_layout.addWidget(self.scraping_operations_group)

        # Analysis Operations Group
        self.analysis_operations_group = QGroupBox("Analysis Operations")
        self.analysis_operations_layout = QHBoxLayout()
        self.view_aggregated_button = QPushButton("👁️‍🗨️ View Aggregated Articles")
        self.view_aggregated_button.clicked.connect(self.view_aggregated_content)
        self.visualize_network_button = QPushButton("🌐  Visualize Network")
        self.visualize_network_button.clicked.connect(self.visualize_network)
        self.analyze_topics_button = QPushButton("👨🏻‍💻 Analyze Topics")
        self.analyze_topics_button.clicked.connect(self.analyze_topics)
        self.generate_report_button = QPushButton("📄 Generate Report")
        self.generate_report_button.clicked.connect(self.generate_report)
        self.export_data_button = QPushButton("💾 Export Data")
        self.export_data_button.clicked.connect(self.export_data)

        self.analysis_operations_layout.addWidget(self.view_aggregated_button)
        self.analysis_operations_layout.addWidget(self.visualize_network_button)
        self.analysis_operations_layout.addWidget(self.analyze_topics_button)
        self.analysis_operations_layout.addWidget(self.generate_report_button)
        self.analysis_operations_layout.addWidget(self.export_data_button)
        self.analysis_operations_group.setLayout(self.analysis_operations_layout)
        self.main_layout.addWidget(self.analysis_operations_group)

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("Scraped results will appear here...")
        self.main_layout.addWidget(self.results_display)

        # State tracking
        self.all_selected = False
        self.scraped_content = {}

    def toggle_select_all(self):
        """Toggle all checkboxes."""
        self.all_selected = not self.all_selected
        state = self.all_selected
        for checkbox in [self.checkbox_foxnews, self.checkbox_philstar, self.checkbox_manilaTimes, self.checkbox_rappler]:
            checkbox.setChecked(state)
        self.check_all_button.setText("Unselect All Websites" if state else "Select All Websites")

    def scrape_websites(self):
        """Scrape selected websites and display results."""
        self.results_display.clear()
        if not any([
            self.checkbox_foxnews.isChecked(),
            self.checkbox_philstar.isChecked(),
            self.checkbox_manilaTimes.isChecked(),
            self.checkbox_rappler.isChecked()
        ]):
            self.results_display.append("<b>Error:</b> No website selected. Please choose a website.")
            return

        self.scraped_content = {}
        websites = [
            ("Fox News", self.checkbox_foxnews.isChecked(), scrape_foxnews),
            ("Philstar", self.checkbox_philstar.isChecked(), scrape_philstar),
            ("Manila Times", self.checkbox_manilaTimes.isChecked(), scrape_manilaTimes),
            ("Rappler", self.checkbox_rappler.isChecked(), scrape_rappler),
        ]

        self.results_display.append(f"<b>Scraping articles...</b>")

        for name, is_checked, scraper in websites:
            if is_checked:
                try:
                    self.scraped_content[name] = scraper()
                    self.results_display.append(f"{name}: {len(self.scraped_content[name])} articles scraped.")
                except Exception as e:
                    self.results_display.append(f"{name}: Failed to scrape. ({str(e)})")

        self.results_display.append("\n<b>Scraping complete.</b>")

    def visualize_network(self):
        """Visualize the network of common articles across news sources."""
        if not self.scraped_content:
            self.results_display.append("<b>Error:</b> No content to visualize. Scrape websites first.")
            return

        # Open the VisualizeNetworkDialog
        dialog = VisualizeNetworkDialog(self.scraped_content, self)
        dialog.exec_()

    def analyze_topics(self):
        """Analyze topics from aggregated articles using LDA and dynamic matching."""
        if not self.scraped_content:
            self.results_display.append("<b>Error:</b> No content to analyze. Scrape websites first.")
            return

        # Open dynamic dialog for topic analysis
        dialog = TopicAnalysisDialog(self.scraped_content, self)
        dialog.exec_()

    def generate_report(self):
        """Placeholder for Generate Report functionality."""
        self.results_display.append("<b>Generating Report...</b> (Feature not yet implemented)")

    def export_data(self):
        """Placeholder for Export Data functionality."""
        self.results_display.append("<b>Exporting Data...</b> (Feature not yet implemented)")


    def view_aggregated_content(self):
        """Display aggregated articles."""
        if not self.scraped_content:
            self.results_display.append("<b>Error:</b> No content to display. Scrape websites first.")
            return

        dialog = ContentDialog("Aggregated Articles", self.scraped_content, self)
        dialog.exec_()

class ContentDialog(QDialog):
    def __init__(self, title, aggregated_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)

        # Main layout
        self.aggregated_content = aggregated_content
        self.layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type to search articles...")
        self.search_button = QPushButton("🔍")
        self.search_button.clicked.connect(self.perform_search)
        self.clear_button = QPushButton("🔄")
        self.clear_button.clicked.connect(self.clear_search)
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_button)
        self.layout.addLayout(search_layout)

        # Tab view for content
        self.tabs = QTabWidget()

        # Create "All Articles" tab first
        self.all_articles_tab = QWidget()
        self.all_articles_layout = QVBoxLayout(self.all_articles_tab)
        self.all_articles_display = QTextEdit()
        self.all_articles_display.setReadOnly(True)

        # Combine all articles into one list
        self.combined_articles = []
        for articles in aggregated_content.values():
            self.combined_articles.extend(articles)

        # Display all articles in the "All Articles" tab
        self.all_articles_display.setText("\n".join(self.combined_articles))
        self.all_articles_layout.addWidget(self.all_articles_display)

        # Add "All Articles" tab as the first tab
        self.tabs.addTab(self.all_articles_tab, "All Articles")

        # Add source-specific tabs
        self.source_displays = {}
        for source, articles in aggregated_content.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            text_display = QTextEdit()
            text_display.setReadOnly(True)
            text_display.setText("\n".join(articles))
            tab_layout.addWidget(text_display)
            self.tabs.addTab(tab, source)
            self.source_displays[source] = text_display

        # Add tabs to layout
        self.layout.addWidget(self.tabs)

    def perform_search(self):
        """Search articles and update the display."""
        query = self.search_field.text().strip().lower()
        if not query:
            return

        # Determine current tab
        current_tab_index = self.tabs.currentIndex()
        current_tab_name = self.tabs.tabText(current_tab_index)

        no_results_message = f"<i>There's no articles matching '{query}' for today.</i>"

        if current_tab_name == "All Articles":
            # Filter all articles
            filtered = [article for article in self.combined_articles if query in article.lower()]
            if filtered:
                self.all_articles_display.setText("\n".join(filtered))
            else:
                self.all_articles_display.setText(no_results_message)
        else:
            # Filter articles for the specific source
            source_articles = self.aggregated_content.get(current_tab_name, [])
            filtered = [article for article in source_articles if query in article.lower()]
            if current_tab_name in self.source_displays:
                if filtered:
                    self.source_displays[current_tab_name].setText("\n".join(filtered))
                else:
                    self.source_displays[current_tab_name].setText(no_results_message)


    def clear_search(self):
        """Clear search and reset all tabs to original content."""
        self.search_field.clear()

        # Reset "All Articles" tab
        self.all_articles_display.setText("\n".join(self.combined_articles))

        # Reset each source-specific tab
        for source, articles in self.aggregated_content.items():
            if source in self.source_displays:
                self.source_displays[source].setText("\n".join(articles))

class TopicAnalysisDialog(QDialog):
    def __init__(self, scraped_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Topic Analysis")
        self.resize(900, 750)

        # Save scraped content
        self.scraped_content = scraped_content

        # Create a vertical layout
        self.layout = QVBoxLayout(self)

        # Add header and description
        date = datetime.now().strftime("%B %d, %Y")  # Current date
        header = QLabel(f"<h2>Topic Analysis for {date}</h2>")
        description = QLabel(
            "<p><i>This analysis uses <b>Latent Dirichlet Allocation (LDA)</b> to extract topics from articles. "
            "Please note that the topic distribution is an approximation and may not be fully accurate.</i></p>"
        )
        header.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)

        # Add header and description to the layout
        self.layout.addWidget(header)
        self.layout.addWidget(description)

        # Dropdown for selecting the news source
        self.layout.addWidget(QLabel("Select News Source:"))  # Proper label for combobox
        self.source_dropdown = QComboBox()
        self.source_dropdown.addItem("All Sources")
        self.source_dropdown.addItems(self.scraped_content.keys())
        self.source_dropdown.currentTextChanged.connect(self.update_graph)
        self.layout.addWidget(self.source_dropdown)

        # Placeholder for graph
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Initial graph generation
        self.update_graph()

    def preprocess_articles(self, articles):
        """Preprocess articles for topic modeling."""
        stop_words = set(stopwords.words('english'))
        processed_articles = []
        for article in articles:
            tokens = word_tokenize(article.lower())  # Tokenize and lowercase
            tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
            processed_articles.append(tokens)
        return processed_articles

    def update_graph(self):
        """Update the graph dynamically based on the selected news source."""
        selected_source = self.source_dropdown.currentText()

        # Combine articles based on the user's choice
        if selected_source == "All Sources":
            combined_articles = []
            for articles in self.scraped_content.values():
                combined_articles.extend(articles)
        else:
            combined_articles = self.scraped_content.get(selected_source, [])

        if not combined_articles:
            self.ax.clear()
            self.ax.set_title(f"No articles available for {selected_source}")
            self.canvas.draw()
            return

        # Preprocess articles
        processed_articles = self.preprocess_articles(combined_articles)

        # Create Dictionary and Corpus
        dictionary = Dictionary(processed_articles)
        corpus = [dictionary.doc2bow(text) for text in processed_articles]

        # Train LDA model
        try:
            lda_model = LdaModel(corpus, num_topics=5, id2word=dictionary, passes=15)
        except Exception as e:
            self.ax.clear()
            self.ax.set_title(f"Error during topic modeling: {str(e)}")
            self.canvas.draw()
            return

        # Extract topics and assign labels
        topics = lda_model.show_topics(num_topics=5, num_words=5, formatted=False)
        labeled_topics = []
        for idx, topic in topics:
            keywords = [word for word, _ in topic]
            label = categorize_topic_dynamic(keywords)  # Map topic to label dynamically
            weight_sum = sum(weight for _, weight in topic)  # Calculate total weight
            labeled_topics.append((label, weight_sum, keywords))

        # Update graph with new data
        self.ax.clear()
        topic_labels = [label for label, _, _ in labeled_topics]
        weights = [weight for _, weight, _ in labeled_topics]

        self.ax.barh(topic_labels, weights, align="center")
        self.ax.set_xlabel("Weight")
        self.ax.set_title(f"Top Topics for {selected_source}")
        self.ax.invert_yaxis()  # Higher weights appear at the top
        self.canvas.draw()

class VisualizeNetworkDialog(QDialog):
    def __init__(self, scraped_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualize Network")
        self.resize(1200, 900)

        # Save scraped content
        self.scraped_content = scraped_content

        # Main layout for the dialog
        self.layout = QVBoxLayout(self)

        # Placeholder for the network graph
        self.figure, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Generate and display the network graph
        self.G, self.pos, self.labels, self.node_types = self.generate_network_graph()

        # Connect hover event for article nodes
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

class VisualizeNetworkDialog(QDialog):
    def __init__(self, scraped_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualize Network")
        self.resize(900, 900)

        # Save scraped content
        self.scraped_content = scraped_content

        # Main layout for the dialog
        self.layout = QVBoxLayout(self)

        # Add directions and labels at the top
        self.directions = QLabel(
            "<h3>News Articles Network</h3>"
            "<p>Below shows the common news articles between news sources.</p>"
            "<p><b style='color:blue;'>BLUE NODES</b>: Represent news sources such as Fox News, Philstar, etc.</p>"
            "<p><b style='color:green;'>GREEN NODES</b>: Represent common news articles shared between sources.</p>"
            "<p>Hover on the corresponding <b style='color:green;'>green nodes</b> to see the full title.</p>"
            "<p><i>Some common articles may be disregarded due to extreme variations on wordings and formattings.</i></p>"
        )
        self.directions.setWordWrap(True)
        self.layout.addWidget(self.directions)

        # Placeholder for the network graph
        self.figure, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Generate and display the network graph
        self.G, self.pos, self.labels, self.node_types = self.generate_network_graph()

        # Connect hover event for article nodes
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def generate_network_graph(self):
        """Create and display a network graph of common articles."""
        if not self.scraped_content:
            self.ax.clear()
            self.ax.set_title("No data available to visualize.")
            self.canvas.draw()
            return None, None, None, None

        # Build the network graph
        G = nx.Graph()
        sources = list(self.scraped_content.keys())
        labels = {}  # Dictionary to map nodes to labels for hover
        node_types = {}  # Dictionary to distinguish between sources and articles

        # Add nodes for each source
        for source in sources:
            G.add_node(source, type='source', color='lightblue')
            labels[source] = source  # Use source name as its label
            node_types[source] = "source"

        # Compare articles and add common articles as nodes and edges
        for i, source1 in enumerate(sources):
            for source2 in sources[i + 1:]:
                for article1 in self.scraped_content[source1]:
                    for article2 in self.scraped_content[source2]:
                        if self.has_significant_word_overlap(article1, article2):
                            truncated_title = self.truncate_text(article1)
                            G.add_node(truncated_title, type='article', color='lightgreen')
                            G.add_edge(source1, truncated_title)
                            G.add_edge(source2, truncated_title)
                            labels[truncated_title] = article1  # Store full article title for hover
                            node_types[truncated_title] = "article"

        # Visualization: Extract node colors
        node_colors = [G.nodes[node].get('color', 'gray') for node in G.nodes]
        pos = nx.spring_layout(G, k=0.5, seed=42)  # Layout for graph

        # Clear the previous graph
        self.ax.clear()
        self.ax.set_title("News Articles Network")

        # Separate labels for sources (displayed) and articles (hover only)
        source_labels = {node: node for node in G.nodes if node_types.get(node) == "source"}

        # Draw the graph
        nx.draw_networkx_nodes(
            G, pos, nodelist=G.nodes, ax=self.ax,
            node_color=node_colors, node_size=600
        )
        nx.draw_networkx_edges(G, pos, ax=self.ax, edge_color="lightgray")

        # Draw labels for source nodes only
        nx.draw_networkx_labels(G, pos, labels=source_labels, font_size=10, font_weight="bold", ax=self.ax)

        # Add legend for blue and green nodes
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightblue', edgecolor='black', label='News Sources (Blue Nodes)'),
            Patch(facecolor='lightgreen', edgecolor='black', label='Shared Articles (Green Nodes)')
        ]
        self.ax.legend(handles=legend_elements, loc="best")

        # Render the canvas
        self.canvas.draw()
        return G, pos, labels, node_types

    def has_significant_word_overlap(self, title1, title2):
        """Check if two article titles have at least 4 words in common."""
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        common_words = words1 & words2
        return len(common_words) >= 4

    def truncate_text(self, text, max_length=50):
        """Truncate long text to fit within the graph."""
        return text if len(text) <= max_length else text[:max_length] + "..."

    def on_hover(self, event):
        """Show the full title of article nodes when hovered."""
        if event.inaxes == self.ax:
            for node, (x, y) in self.pos.items():
                if abs(x - event.xdata) < 0.05 and abs(y - event.ydata) < 0.05:
                    node_type = self.node_types.get(node)
                    if node_type == "article":
                        # Display the full article title in the plot's title
                        tooltip = self.labels.get(node, "")
                        self.ax.set_title(f"{tooltip}")
                        self.canvas.draw()
                        return  # Exit after showing the first match
            # Reset the title if no match is found
            self.ax.set_title("News Articles Network")
            self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
