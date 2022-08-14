import disnake
import random


class blackjack(disnake.ui.View):
    def __init__(self, inter:disnake.CommandInteraction, bot_name):
        super().__init__(timeout=20)
        self.inter = inter
        self.cards = {"A" : 1, "2" : 2, "3" : 3, "4" : 4, "5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9, "10" : 10, "J" : 10, "Q" : 10, "K" : 10}
        self.suits = ["♤","♧","♢","♡"]
        self.used_cards = []
        self.user_cards = [self.get_random_card(),self.get_random_card()]
        self.bot_cards = [self.get_random_card(), "?"]
        self.bot_name = bot_name
        self.game_finished = False
        
    def get_total(self, cards:list):
        total = 0
        print(cards)
        for card in cards:
            if card[1:] == "A": #Checks whether A should automatically be assigned to a 1 or 11
                if total <= 10:
                    value_of_card =11
                else:
                    value_of_card = 1
            else:
                value_of_card = self.cards[card[1:]]
                
            total += value_of_card
        return total

    def get_random_card(self):
        # print(list(self.cards.keys()))
        while True:
            card = random.choice(list(self.cards.keys()))
            suit = random.choice(self.suits)
            card = suit+card
            if card not in self.used_cards:
                self.used_cards.append(card)
                return card
        
            
    def gen_embed(self, user:disnake.Member, bot_name, user_cards:list, bot_cards:list, description="", game_ended=False):
        if not game_ended:
            bot_total = "?"
        else:
            bot_total = self.get_total(bot_cards)
        embed = disnake.Embed(description=description)
        user_cards_list = user_cards
        bot_cards_list = bot_cards
        user_cards_string = " ".join(user_cards_list)
        user_total = self.get_total(user_cards_list)
        bot_cards_string = " ".join(bot_cards_list)
        embed.set_author(name=f"{user.name}'s blackjack game", icon_url=user.display_avatar)
        embed.add_field(name=f"**{user.name} (Player)**", value= f"Cards - **{user_cards_string}**\nTotal - `{user_total}`")
        embed.add_field(name=f"**{bot_name} (Dealer)**", value= f"Cards - **{bot_cards_string}**\nTotal - `{bot_total}`")
        return embed
        
    @disnake.ui.button(label="Hit", style=disnake.ButtonStyle.blurple)
    async def hit(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author.id == self.inter.author.id:
            self.user_cards.append(self.get_random_card())
            user_total = self.get_total(self.user_cards)
            if user_total == 21:
                description = ""
                self.bot_cards.pop(-1)
                while True:
                    self.bot_cards.append(self.get_random_card())
                    bot_total = self.get_total(self.bot_cards)
                    if bot_total == user_total:
                        description += "Ended up in a draw"
                        break
                    else:
                        description += "You have won! Congratulations."
                        break
                self.hit.disabled = True
                self.stand.disabled = True
                embed = self.gen_embed(interaction.author, self.bot_name, self.user_cards, self.bot_cards, description=description, game_ended=True)
                await interaction.response.edit_message(embed=embed, view=self)
                self.game_finished = True
                
            if user_total > 21:
                description = "You lost!"
                self.bot_cards.pop(-1)
                self.bot_cards.append(self.get_random_card())
                self.hit.disabled = True
                self.stand.disabled = True
                embed = self.gen_embed(interaction.author, self.bot_name, self.user_cards, self.bot_cards, description = description, game_ended = True)
                await interaction.response.edit_message(embed=embed, view=self)
                self.game_finished = True
                
            if user_total < 21:
                embed = self.gen_embed(interaction.author, self.bot_name, self.user_cards, self.bot_cards)
                await interaction.response.edit_message(embed=embed, view=self)
                self.game_finished = True
        else:
            await interaction.response.send_message(f"That is not your blackjack game", ephemeral=True)
            
            

    @disnake.ui.button(label="Stand", style=disnake.ButtonStyle.blurple)
    async def stand(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author.id == self.inter.author.id:
            user_total = self.get_total(self.user_cards)
            description = ""
            self.bot_cards.pop(-1)
            while True:
                self.bot_cards.append(self.get_random_card())
                bot_total = self.get_total(self.bot_cards)
                if bot_total <= 21:
                    if bot_total > user_total:
                        description += "You lost!"
                        break
                    if bot_total == user_total:
                        if bot_total == 21:
                            description += "Ended up in a draw."
                            break
                else:
                    description += "You won!"
                    break
                    
            self.hit.disabled = True
            self.stand.disabled = True
            embed = self.gen_embed(interaction.author, self.bot_name, self.user_cards, self.bot_cards, description=description, game_ended = True)
            await interaction.response.edit_message(embed=embed, view=self)
            self.game_finished = True
            
        else:
            await interaction.response.send_message(f"That is not your blackjack game", ephemeral=True)
            
                
        
    async def on_timeout(self):
        if not self.game_finished:
            self.hit.disabled = True
            self.stand.disabled = True
            await self.inter.edit_original_message("You haven't responded in time.", view=self)