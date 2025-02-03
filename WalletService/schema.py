import graphene
import Wallet.schema


class Query(Wallet.schema.Query, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)