import mysql.connector
from mysql.connector import Error

# Database configuration - update these values to match your database
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'book_engine',
    'raise_on_warnings': True
}

# Sample story content for some popular books
sample_stories = {
    "Harry Potter and the Sorcerer's Stone": """Chapter 1: The Boy Who Lived

Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious, because they just didn't hold with such nonsense.

Mr. Dursley was the director of a firm called Grunnings, which made drills. He was a big, beefy man with hardly any neck, although he did have a very large mustache. Mrs. Dursley was thin and blonde and had nearly twice the usual amount of neck, which came in very useful as she spent so much of her time craning over garden fences, spying on the neighbors.

The Dursleys had a small son called Dudley and in their opinion there was no finer boy anywhere.

The Dursleys had everything they wanted, but they also had a secret, and their greatest fear was that somebody would discover it. They didn't think they could bear it if anyone found out about the Potters.

Mrs. Potter was Mrs. Dursley's sister, but they hadn't met for several years; in fact, Mrs. Dursley pretended she didn't have a sister, because her sister and her good-for-nothing husband were as unDursleyish as it was possible to be. The Dursleys shuddered to think what the neighbors would say if the Potters arrived in the street. The Dursleys knew that the Potters had a small son, too, but they had never even seen him.

This boy was another good reason for keeping the Potters away; they didn't want Dudley mixing with a child like that.

When Mr. and Mrs. Dursley woke up on the dull, gray Tuesday our story starts, there was nothing about the cloudy sky outside to suggest that strange and mysterious things would soon be happening all over the country.

Mr. Dursley hummed as he picked out his most boring tie for work, and Mrs. Dursley gossiped away happily as she wrestled a screaming Dudley into his high chair.

None of them noticed a large, tawny owl flutter past the window.

At half past eight, Mr. Dursley picked up his briefcase, pecked Mrs. Dursley on the cheek, and tried to kiss Dudley good-bye but missed, because Dudley was now having a tantrum and throwing his cereal at the walls.

"Little tyke," chortled Mr. Dursley as he left the house. He got into his car and backed out of number four's drive.

It was on the corner of the street that he noticed the first sign of something peculiar -- a cat reading a map. For a second, Mr. Dursley didn't realize what he had seen -- then he jerked his head around to look again. There was a tabby cat standing on the corner of Privet Drive, but there wasn't a map in sight. What could he have been thinking of? It must have been a trick of the light. Mr. Dursley blinked and stared at the cat. It stared back. As Mr. Dursley drove around the corner and up the road, he watched the cat in his mirror. It was now reading the sign that said Privet Drive -- no, looking at the sign; cats couldn't read maps or signs. Mr. Dursley gave himself a little shake and put the cat out of his mind. As he drove toward town he thought of nothing except a large order of drills he was hoping to get that day.

But on the edge of town, drills were driven out of his mind by something else. As he sat in the usual morning traffic jam, he couldn't help noticing that there seemed to be a lot of strangely dressed people about. People in cloaks. Mr. Dursley couldn't bear people who dressed in funny clothes -- the getups you saw on young people! He supposed this was some stupid new fashion. He drummed his fingers on the steering wheel and his eyes fell on a huddle of these weirdos standing quite close by. They were whispering excitedly together. Mr. Dursley was enraged to see that a couple of them weren't young at all; why, that man had to be older than he was, and wearing an emerald-green cloak! The nerve of him! But then it struck Mr. Dursley that this was probably some silly stunt -- these people were obviously collecting for something... yes, that would be it. The traffic moved on and a few minutes later, Mr. Dursley arrived in the Grunnings parking lot, his mind back on drills.

Mr. Dursley always sat with his back to the window in his office on the ninth floor. If he hadn't, he might have found it harder to concentrate on drills that morning. He didn't see the owls swooping past in broad daylight, though people down in the street did; they pointed and gazed open-mouthed as owl after owl sped overhead. Most of them had never seen an owl even at nighttime. Mr. Dursley, however, had a perfectly normal, owl-free morning. He yelled at five different people. He made several important telephone calls and shouted a bit more. He was in a very good mood until lunchtime, when he thought he'd stretch his legs and walk across the road to buy himself a bun from the bakery.

He'd forgotten all about the people in cloaks until he passed a group of them next to the baker's. He eyed them angrily as he passed. He didn't know why, but they made him uneasy. This bunch were whispering excitedly, too, and he couldn't see a single collecting tin. It was on his way back past them, clutching a large doughnut in a bag, that he caught a few words of what they were saying.

"The Potters, that's right, that's what I heard --"

"-- yes, their son, Harry --"

Mr. Dursley stopped dead. Fear flooded him. He looked back at the whisperers as if he wanted to say something to them, but thought better of it.

He dashed back across the road, hurried up to his office, snapped at his secretary not to disturb him, seized his telephone, and had almost finished dialing his home number when he changed his mind. He put the receiver back down and stroked his mustache, thinking... no, he was being stupid. Potter wasn't such an unusual name. He was sure there were lots of people called Potter who had a son called Harry. Come to think of it, he wasn't even sure his nephew was called Harry. He'd never even seen the boy. It might have been Harvey. Or Harold. There was no point in worrying Mrs. Dursley; she always got so upset at any mention of her sister. He didn't blame her, if he'd had a sister like that... but all the same, those people in cloaks...

He found it a lot harder to concentrate on drills that afternoon and when he left the building at five o'clock, he was still so worried that he walked straight into someone just outside the door.

"Sorry," he grunted, as the tiny old man stumbled and almost fell. It was a few seconds before Mr. Dursley realized that the man was wearing a violet cloak. He didn't seem at all upset at being almost knocked to the ground. On the contrary, his face split into a wide smile and he said in a squeaky voice that made passersby stare, "Don't be sorry, my dear sir, for nothing could upset me today! Rejoice, for You-Know-Who has gone at last! Even Muggles like yourself should be celebrating, this happy, happy day!"

And the old man hugged Mr. Dursley around the middle and walked off.

Mr. Dursley stood rooted to the spot. He had been hugged by a complete stranger. He also thought he had been called a Muggle, whatever that was. He was rattled. He hurried to his car and set off for home, hoping he was imagining things, which he had never hoped before, because he didn't approve of imagination.

As he pulled into the driveway of number four, the first thing he saw -- and it didn't improve his mood -- was the tabby cat he'd spotted that morning. It was now sitting on his garden wall. He was sure it was the same one; it had the same markings around its eyes.

"Shoo!" said Mr. Dursley loudly.

The cat didn't move. It just gave him a stern look. Was this normal cat behavior? Mr. Dursley wondered. Trying to pull himself together, he let himself into the house. He was still determined not to mention anything to his wife.

Mrs. Dursley had had a nice, normal day. She told him over dinner all about Mrs. Next Door's problems with her daughter and how Dudley had learned a new word ("Won't!"). Mr. Dursley tried to act normally. When Dudley had been put to bed, he went into the living room in time to catch the last report on the evening news:

"And finally, bird-watchers everywhere have reported that the nation's owls have been behaving very unusually today. Although owls normally hunt at night and are hardly ever seen in daylight, there have been hundreds of sightings of these birds flying in every direction since sunrise. Experts are unable to explain why the owls have suddenly changed their sleeping pattern." The newscaster allowed himself a grin. "Most mysterious. And now, over to Jim McGuffin with the weather. Going to be any more showers of owls tonight, Jim?"

"Well, Ted," said the weatherman, "I don't know about that, but it's not only the owls that have been acting oddly today. Viewers as far apart as Kent, Yorkshire, and Dundee have been phoning in to tell me that instead of the rain I promised yesterday, they've had a downpour of shooting stars! Perhaps people have been celebrating Bonfire Night early -- it's not until next week, folks! But I can promise a wet night tonight."

Mr. Dursley sat frozen in his armchair. Shooting stars all over Britain? Owls flying by daylight? Mysterious people in cloaks all over the place? And a whisper, a whisper about the Potters...

Mrs. Dursley came into the living room carrying two cups of tea. It was no good. He'd have to say something to her. He cleared his throat nervously. "Er -- Petunia, dear -- you haven't heard from your sister lately, have you?"

As he had expected, Mrs. Dursley looked shocked and angry. After all, they normally pretended she didn't have a sister.

"No," she said sharply. "Why?"

"Funny stuff on the news," Mr. Dursley mumbled. "Owls... shooting stars... and there were a lot of funny-looking people in town today..."

"So?" snapped Mrs. Dursley.

"Well, I just thought... maybe... it was something to do with... you know... her crowd."

Mrs. Dursley went very white. He'd said the wrong thing. She'd jumped to her feet, her face like thunder, and pointing at him, shrieked, "You watch your step, Vernon! You keep your silly remarks to yourself! That lot are nothing but troublemakers! I don't want any of them near my family!"

She seized her teacup and trembling, carried it into the kitchen. Mr. Dursley sat there, shaken to his core. He'd never seen his wife so angry. After a few minutes, she came back with a slightly more composed face, but her eyes were still glittering dangerously.

"They were all waving their banners and chanting," she said, as though he'd pressed her into giving more information. "About You-Know-Who. They think he's coming back." She sniffed angrily. "Crazy fools. You-Know-Who coming back! I suppose if he had, there'd be no need for all this secrecy around that boy. But they don't think they can hide him from me forever. I know what he looks like, Vernon. I know what he looks like."

She fell silent, still staring at him with an expression of mingled fear and hatred. Mr. Dursley had no idea what to say. He poured himself another cup of tea and tried to think of something to say that wouldn't enrage her again. A few minutes later, the teapot was empty, and Mrs. Dursley was still glaring at him. Finally, he said gently, "You don't think they -- You-Know-Who's supporters -- might come after us, do you?"

"I think we should check on the boy," said Mrs. Dursley sharply. "Tomorrow. This could be the day."

"Oh, Petunia, dear, it's been ten years. I don't think they're going to come back now," said Mr. Dursley, but he was not entirely confident in his words. He was secretly worried about what tomorrow would bring.

[This is a sample of the full story content. In a real implementation, the complete book text would be stored here.]
""",
    "The Lord of the Rings": """Chapter 1: A Long-expected Party

When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton.

Bilbo was very rich and very peculiar, and had been the wonder of the Shire for sixty years, ever since his remarkable disappearance and unexpected return. The riches he had brought back from his travels had now become a local legend, and it was popularly believed, whatever the old folk might say, that the Hill at Bag End was full of tunnels stuffed with treasure.

At the top of the Hill, Bag End was just the sort of house that hobbits love, round-faced and round-doored and round-windowed, with a garden and a short green path leading to the door. It was built into the Hill, as hobbits say, or burrowed if you prefer. Whichever expression you use, it meant that the front door was at the side, in the middle of a grassy hillside, with a round brass knob exactly in the middle of it.

The hole was filled with the sound of voices when Bilbo Baggins invited his friends to tea. There was a constant stream of visitors at the door, and a steady hum of conversation inside. The party was going full swing, and old Bilbo was in his element, greeting guests with his usual hospitality.

As the evening wore on, Bilbo surprised everyone by announcing that he was going on another adventure. The hobbits were astounded, but before they could protest, Bilbo had disappeared, leaving behind only his ring and a note explaining that he had gone off to visit the elves.

[This is a sample of the full story content. In a real implementation, the complete book text would be stored here.]""",
    "Pride and Prejudice": """Chapter 1: It is a truth universally acknowledged

It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.

However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.

"My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"

Mr. Bennet replied that he had not.

"But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."

Mr. Bennet made no answer.

"Do you not want to know who has taken it?" cried his wife impatiently.

"You want to tell me, and I have no objection to hearing it."

This was invitation enough.

"Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it, that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house by the end of next week."

"What is his name?"

"Bingley."

"Is he married or single?"

"Oh! Single, my dear, to be sure! A single man of large fortune; four or five thousand a year. What a fine thing for our girls!"

"How so? How can it affect them?"

"My dear Mr. Bennet," replied his wife, "how can you be so tiresome! You must know that I am thinking of his marrying one of them."

"Is that his design in settling here?"

"Design! Nonsense, how can you talk so! But it is very likely that he may fall in love with one of them, and therefore you must visit him as soon as he comes."

"I see no occasion for that. You and the girls may go, or you may send them by themselves, which perhaps will be still better, for as you are as handsome as any of them, Mr. Bingley may like you the best of the party."

[This is a sample of the full story content. In a real implementation, the complete book text would be stored here.]"""
}

try:
    # Connect to the database
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    
    # Update books with sample story content
    for title, story_content in sample_stories.items():
        update_query = "UPDATE book_table SET story_content = %s WHERE title = %s"
        cursor.execute(update_query, (story_content, title))
    
    # Commit the changes
    cnx.commit()
    
    print(f"Successfully updated {cursor.rowcount} books with sample story content.")
    
except Error as e:
    print(f"Error: {e}")
    
finally:
    # Close the connection
    if cnx.is_connected():
        cursor.close()
        cnx.close()
        print("MySQL connection is closed.")