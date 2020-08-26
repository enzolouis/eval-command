# eval-command

<li>English</li>

eval-command is a simple project with no more than 2 or 3 files.

This project use python with discord.py for an eval bot command.

> What's an eval command ?

*It's a command to execute code directly on discord, you could just run simple instruction, or more, asynchronous instructions like create a channel in a guild, ban user, ...
We use it to test our other commands quickly*

`[PREFIX]eval code`

![Use example image command](https://cdn.discordapp.com/attachments/711607976150171691/748192408532942848/unknown.png)
![Use example image output](https://cdn.discordapp.com/attachments/711607976150171691/748193180599713792/unknown.png)

`return` is not always useful with eval command, so if you return something, you will have a description oh the object you return : object representation, type, lenght, dir (method associated with the objet)

Eventually, a single message is sent, with the output (like print, or error), and the return object description if not null. If this message exceeds 2000 characters (discord limit), the whole message is sent to http://bin.lazor.be/ and response sent to you.

After this message, one :boom: reaction appears, if you click on, it will be deleted for more visibility.
