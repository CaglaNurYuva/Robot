import firebase_admin
from firebase_admin import credentials, firestore
from tkinter import Tk, Button
import time

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Global variable for storing ordered entries
ordered_entries = []
orders_ref = None
current_doc_id = None

currentlyProcessedOrder_ref = None
alreadyDeliveredOrders_ref = None

# Function to print the ordered entries one by one
def print_entry():
    global ordered_entries
    if ordered_entries:
        for entry in ordered_entries:
            print(entry)
    else:
        print("No data to print.")
        

def printDelivered_entry():  
    global alreadyDeliveredOrders_ref 
    ordered_entries = [doc.to_dict() for doc in alreadyDeliveredOrders_ref]   
    if ordered_entries:
        for entry in ordered_entries:
            print(entry)
    else:
        print("No data to print.")
    

            
def payment_taken():
    global alreadyDeliveredOrders_ref
    # Query Firestore to find the document where OrderID is equal to "id1"
    for doc in alreadyDeliveredOrders_ref:
        current_id = doc.id
        data = db.collection("alreadyDeliveredOrders").document(current_id).get().to_dict()
        if data.get("OrderID") == "id2":
            db.collection("alreadyDeliveredOrders").document(current_id).delete()
            break


    

# Function to initialize ordered_entries with initial database
def initialize():
    global ordered_entries, orders_ref, currentlyProcessedOrder_ref, alreadyDeliveredOrders_ref
    orders_ref = db.collection("orders").order_by("timestamp").get()
    ordered_entries = [doc.to_dict() for doc in orders_ref]
    # Retrieve documents from Firestore in descending order of timestamp
    currentlyProcessedOrder_ref = db.collection("currentlyProcessedOrder").order_by("timestamp").get()
    alreadyDeliveredOrders_ref = db.collection("alreadyDeliveredOrders").order_by("timestamp").get()

    print("Initialization complete.")

# Function to add a new entry to Firestore
def add_entry():
    order_data = {"OrderID": "id4_added", "fromWhichTable": "table4", "OrderList": "['su', 'tatli']", "Price":100, "orderStatus": "Waiting", "timestamp": firestore.SERVER_TIMESTAMP}
       
    db.collection("orders").add(order_data)
    print("New entry added successfully!")
    
 
 
def create_dataset():
    order_data = [
        {"OrderID": "id1", "fromWhichTable": "table1", "OrderList": "['su', 'tatli']", "Price":100, "orderStatus": "Waiting", "timestamp": firestore.SERVER_TIMESTAMP},
        {"OrderID": "id2", "fromWhichTable": "table2", "OrderList": "['su', 'tatli']", "Price":100, "orderStatus": "Waiting", "timestamp": firestore.SERVER_TIMESTAMP},
        {"OrderID": "id3", "fromWhichTable": "table3", "OrderList": "['su', 'tatli']", "Price":100, "orderStatus": "Waiting", "timestamp": firestore.SERVER_TIMESTAMP}
       
    ]
    
    for order in order_data:
        db.collection("orders").add(order)
        time.sleep(0.015)  # Sleep for 15 milliseconds (0.015 seconds)



    

# Function to handle real-time updates to the Firestore collection
def on_snapshot(col_snapshot, changes, read_time):
    global ordered_entries
    for change in changes:
        if change.type.name == 'ADDED':
            print("New entry added:")
            print(change.document.to_dict())
            initialize()
            
        elif change.type.name == 'MODIFIED':
            print("Entry modified:")
            print(change.document.to_dict())
            initialize()
        
        elif change.type.name == 'REMOVED':
            print("Entry removed:")
            print(change.document.to_dict())  # This will print the data of the removed document
            initialize()  # Handle the removal as needed

          

def handleOrder():
    global current_doc_id, orders_ref
    # Initialize a counter for the number of documents
    num_documents = 0

    # Iterate through the documents and increment the counter
    for doc in orders_ref:
        num_documents += 1
        
    # Check if there are any documents in the snapshot
    if num_documents > 0:
        # Get only the first order from the orders list, thats why break is put immediately
        for docx in orders_ref:
            # Retrieve the first document
        
            current_doc_id = docx.id
            db.collection('orders').document(current_doc_id).update({"orderStatus": "Being processed"})  
            
            data = db.collection("orders").document(current_doc_id).get().to_dict()
            currentlyProcessedData = {
            "OrderID": data.get("OrderID"),
            "fromWhichTable": data.get("fromWhichTable"),
            "Price": data.get("Price"),
            "orderStatus": data.get("orderStatus"),
            "timestamp": firestore.SERVER_TIMESTAMP
            }

            db.collection("currentlyProcessedOrder").add(currentlyProcessedData)
            print("Added to currentlyProcessedData!")
            
             

            # Print the data of the first document
            print(docx.to_dict())
            break
    else:
        print("No documents found")


  
def remove_entry():
    global currentlyProcessedOrder_ref
    doc_ref = db.collection("orders").document(current_doc_id)
    # Get the document snapshot
    doc_snapshot = doc_ref.get()
          
    # Check if the document exists
    if doc_snapshot.exists:
        # Access the data dictionary
        data = doc_snapshot.to_dict()

        goal_data = {
        "fromWhichTable": data.get("fromWhichTable"),
        "timestamp": firestore.SERVER_TIMESTAMP,
        "OrderID": data.get("OrderID"),
        "isUrgent": False
        }
        
        returnToStart_data = {
        "fromWhichTable": "table0",
        "timestamp": firestore.SERVER_TIMESTAMP,
        "OrderID": "none",
        "isUrgent": False
        }

        db.collection("goals").add(goal_data)
        time.sleep(0.015)  # Sleep for 15 milliseconds (0.015 seconds)
        db.collection("goals").add(returnToStart_data)
        print("Added to goals!")

        
        
        
        # Query Firestore to find the document where OrderID is equal to "id1"
        query = db.collection("currentlyProcessedOrder").where("OrderID", "==", data.get("OrderID")).get()

        # Check if any documents match the query
        if query:
            for doc in query:
                new_id = doc.id
                db.collection('currentlyProcessedOrder').document(new_id).update({"orderStatus": "OnItsWay"})
                print("Updated in currentlyProcessedOrder!")
                break
        
        
        else:
            print("No document found with OrderID equal to 'id1'")
            
        
            # burada birden fazla entry varsa, en tepedeki entryi kontrol et/karsilastir, aynı orderID'yi tekrar ekleme
       
            # Mobil appde currentlyProcessedOrder'a bastan sona bak, OrderID var ama ilk sırada degilse orderStatus:"InQueueForRobot" yaz mobil appde.
            # Mobil appde currentlyProcessedOrder'a bastan sona bak, OrderID hiç yoksa orderStatus: "Waiting" yaz mobil appde.
            # Mobil app currentlyProcessedOrder'ın orderStatus'unu "Alındı" olarak değiştirmeli. Bu değişim olduğunda robot sonraki hedef koordinatına gitmeye başlayacak, yani baslangic noktasina.

        doc_ref.delete()
        print("Removed from orders!")            
       
    else:
        print(f"Document with ID {current_doc_id} does not exist.")
          
	  
def update_order_status(new_id):
    # Query Firestore to find the document where OrderID is equal to new_id
    query = db.collection("currentlyProcessedOrder").where("OrderID", "==", new_id).get()

    # Check if any documents match the query
    if query:
        for doc in query:
            # Update the document's orderStatus field to "Ready"
            doc_ref = db.collection("currentlyProcessedOrder").document(doc.id)
            doc_ref.update({"orderStatus": "Ready"})
            print(f"Order with OrderID '{new_id}' has been updated to 'Ready'")
    else:
        print(f"No document found with OrderID equal to '{new_id}'")
	  
          
          
def update_flag():
    global currentlyProcessedOrder_ref
    
    
    doc_ref = db.collection("orders").document(current_doc_id)
    doc_ref.update({"orderStatus": "Ready"})
    
     # Get the document snapshot
    doc_snapshot = doc_ref.get()
          
    # Check if the document exists
    if doc_snapshot.exists:
        # Access the data dictionary
        data = doc_snapshot.to_dict()
    
    
        new_id = data.get("OrderID")
        # Find entry whose OrderID is equal to new_id, update that entry's orderStatus as "Ready", the name of database is "currentlyProcessedOrder"
        update_order_status(new_id)
        #db.collection('currentlyProcessedOrder').document(new_id).update({"orderStatus": "Ready"})
            


# Create a listener for real-time updates to the Firestore collection
def monitor_collection():
    global orders_ref
    orders_ref = db.collection("orders")
    orders_watch = orders_ref.on_snapshot(on_snapshot)

# Create GUI
root = Tk()
root.title("Firestore Desktop App")

# Add Button
add_button = Button(root, text="Add", command=add_entry)
add_button.pack()

remove_button = Button(root, text="Remove the order from being prepared orders list", command=remove_entry)
remove_button.pack()

handle_button = Button(root, text="Get Next Order To Process", command=handleOrder)
handle_button.pack()

update_button = Button(root, text="Order is put on the robot! Set order status as ready!", command=update_flag)
update_button.pack()

# Print Button
print_button = Button(root, text="Print All Current Orders", command=print_entry)
print_button.pack()

printDelivered_button = Button(root, text="Print All Already Delivered Orders", command=printDelivered_entry)
printDelivered_button.pack()

payment_button = Button(root, text="Payment is taken for the order with id2", command=payment_taken)
payment_button.pack()

# Exit Button
exit_button = Button(root, text="Exit", command=root.quit)
exit_button.pack()

# Initialize ordered_entries with initial database at the start of the program
initialize()

# Start monitoring the Firestore collection for real-time updates
monitor_collection()
create_dataset()
# Start the Tkinter event loop
root.mainloop()

