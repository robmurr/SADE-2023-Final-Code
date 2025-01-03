import pygame
from PongWithClasses import pong
import neat
import os
import pickle


class PongGame:
    def __init__(self):
        self.game = pong.Game()
        self.game.initialize()
        self.right_paddle = self.game.player1
        self.left_paddle = self.game.player2
        self.ball = self.game.ball

    def test_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        run = True
        clock = pygame.time.Clock()
        while run:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

            # This code is for playing against the AI yourself
            # keys = pygame.key.get_pressed()
            # if keys[pygame.K_UP]:
                # self.right_paddle.move_up()
            # elif keys[pygame.K_DOWN]:
                # self.right_paddle.move_down()

            # This code is for having a "computer" player play against the AI
            if self.right_paddle.y + pong.PADDLE_HEIGHT // 2 < self.ball.y:
                self.right_paddle.move_down()
            elif self.right_paddle.y + pong.PADDLE_HEIGHT // 2 > self.ball.y:
                self.right_paddle.move_up()

            output = net.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x - self.ball.x)))
            decision = output.index(max(output))

            if decision == 0:
                pass
            elif decision == 1:
                self.left_paddle.move_up()
            else:
                self.left_paddle.move_down()

            game_info = self.game.loop()
            # print(game_info.player2_hits, game_info.player1_hits, game_info.player2_score, game_info.player1_score)
            self.game.draw()

    def train_ai(self, genome1, genome2, config):
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

            output1 = net1.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
            decision1 = output1.index(max(output1))

            if decision1 == 0:
                pass
            elif decision1 == 1:
                self.right_paddle.move_up()
            else:
                self.right_paddle.move_down()

            output2 = net2.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x - self.ball.x)))
            decision2 = output2.index(max(output2))

            if decision2 == 0:
                pass
            elif decision2 == 1:
                self.left_paddle.move_up()
            else:
                self.left_paddle.move_down()

            game_info = self.game.loop()

            self.game.draw()

            if game_info.player1_score >= 1 or game_info.player2_score >= 1 or game_info.player1_hits > 50:
                self.calculate_fitness(genome1, genome2, game_info)
                break

    def calculate_fitness(self, genome1, genome2, game_info):
        genome1.fitness += game_info.player1_hits
        genome2.fitness += game_info.player2_hits


def eval_genomes(genomes, config):
    for i, (genome_id1, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 0
        for genome_id2, genome2 in genomes[i+1:]:
            genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
            game = PongGame()
            game.train_ai(genome1, genome2, config)


def run_neat(config):
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-0')  # starts at a saved checkpoint
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))  # saves a checkpoint after every nth generation

    winner = p.run(eval_genomes, 50)
    # returns either the best genome after n generations or the first one to reach the fitness threshold
    with open('best.pickle', 'wb') as f:
        pickle.dump(winner, f)


def test_ai(config):
    with open('best.pickle', 'rb') as f:
        winner = pickle.load(f)

    game = PongGame()
    game.test_ai(winner, config)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # run_neat(config)
    test_ai(config)
